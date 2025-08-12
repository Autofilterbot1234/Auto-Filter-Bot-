import datetime
import motor.motor_asyncio
from info import DATABASE_URIS, DATABASE_NAME

class Database:
    def __init__(self):
        # প্রথম URI টি প্রধান ক্লায়েন্ট হিসেবে ব্যবহৃত হবে
        self._client = motor.motor_asyncio.AsyncIOMotorClient(DATABASE_URIS[0])
        self.db = self._client[DATABASE_NAME]
        
        # কালেকশনগুলো সংজ্ঞায়িত করা হচ্ছে
        self.users = self.db.users
        self.chats = self.db.chats
        self.fsub = self.db.fsub_channels
        self.join_requests = self.db.join_requests

    # --- ব্যবহারকারী সম্পর্কিত ফাংশন ---
    async def add_user(self, id, name):
        user = dict(
            id = id,
            name = name,
            ban_status=dict(is_banned=False, ban_reason=""),
            verify_expiry=None,
            is_approved_in_private=False
        )
        await self.users.insert_one(user)

    async def is_user_exist(self, id):
        return bool(await self.users.find_one({'id': int(id)}))

    async def total_users_count(self):
        return await self.users.count_documents({})

    async def get_all_users(self):
        return self.users.find({})

    async def ban_user(self, user_id, reason):
        await self.users.update_one({'id': user_id}, {'$set': {'ban_status': {'is_banned': True, 'ban_reason': reason}}})

    async def remove_ban(self, user_id):
        await self.users.update_one({'id': user_id}, {'$set': {'ban_status': {'is_banned': False, 'ban_reason': ''}}})

    # --- চ্যাট সম্পর্কিত ফাংশন ---
    async def add_chat(self, id, title):
        chat = dict(id=id, title=title)
        await self.chats.insert_one(chat)

    async def get_chat(self, id):
        return await self.chats.find_one({'id': int(id)})

    async def total_chat_count(self):
        return await self.chats.count_documents({})

    async def get_all_chats(self):
        return self.chats.find({})

    # --- ফোর্স সাবস্ক্রাইব সম্পর্কিত ফাংশন ---
    async def add_fsub_channel(self, channel_id, channel_type="public"):
        await self.fsub.insert_one({'channel_id': int(channel_id), 'channel_type': channel_type})

    async def remove_fsub_channel(self, channel_id):
        await self.fsub.delete_one({'channel_id': int(channel_id)})

    async def get_fsub_channels(self):
        channels = self.fsub.find({})
        public_channels, private_channels = [], []
        async for channel in channels:
            if channel.get('channel_type') == 'private':
                private_channels.append(channel['channel_id'])
            else:
                public_channels.append(channel['channel_id'])
        return public_channels, private_channels

    async def is_fsub_channel_exist(self, channel_id):
        return bool(await self.fsub.find_one({'channel_id': int(channel_id)}))

    # --- জয়েন রিকোয়েস্ট সম্পর্কিত ফাংশন ---
    async def add_join_request(self, user_id, channel_id):
        await self.join_requests.update_one(
            {'user_id': int(user_id)},
            {'$addToSet': {'requested_channels': int(channel_id)}},
            upsert=True
        )

    async def has_sent_join_request(self, user_id, channel_id):
        user_data = await self.join_requests.find_one({'user_id': int(user_id)})
        if user_data and 'requested_channels' in user_data:
            return int(channel_id) in user_data['requested_channels']
        return False
        
    # --- ভেরিফিকেশন সম্পর্কিত ফাংশন ---
    async def update_verify_status(self, user_id, expiry_time):
        await self.users.update_one({'id': int(user_id)}, {'$set': {'verify_expiry': expiry_time}}, upsert=True)

    async def get_verify_status(self, user_id):
        user = await self.users.find_one({'id': int(user_id)})
        return user.get('verify_expiry') if user else None

# ডাটাবেস ক্লাসের একটি ইনস্ট্যান্স তৈরি করা হচ্ছে
db = Database()
