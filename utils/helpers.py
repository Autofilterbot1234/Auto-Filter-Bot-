import re
import random
import secrets
import string
import asyncio
import aiohttp
import datetime
from pyrogram.errors import UserNotParticipant
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from info import (
    FSUB_PICS, GRP_LNK, OWNER_LNK,
    IS_SHORTLINK, SHORTLINK_URL, SHORTLINK_API, TUTORIAL,
    VERIFY, VERIFY_EXPIRE, HOW_TO_VERIFY, FQDN
)
from database.users_chats_db import db
from utils.temp import temp # একটি অস্থায়ী ডেটা স্টোর করার জন্য

# --- ভেরিফিকেশন সিস্টেমের জন্য গ্লোবাল ডিকশনারি ---
VERIFY_TOKENS = {}

def get_size(size_bytes):
    """বাইটকে মানুষের পাঠযোগ্য ফরম্যাটে (KB, MB, GB) রূপান্তর করে"""
    if not size_bytes:
        return ""
    power = 1024
    n = 0
    power_labels = {0: '', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size_bytes > power and n < len(power_labels) -1 :
        size_bytes /= power
        n += 1
    return f"{size_bytes:.2f} {power_labels[n]}"

def unpack_new_file_id(file_id):
    """নতুন ফাইল আইডি থেকে মিডিয়া আইডি এবং অ্যাক্সেস হ্যাশ বের করে"""
    # এই ফাংশনটি আগের কোড থেকে নেওয়া হয়েছে এবং এটি ফাইল আইডি ডিকোড করার জন্য প্রয়োজন
    # এখানে কোনো পরিবর্তনের দরকার নেই
    try:
        from pyrogram.file_id import FileId
        decoded = FileId.decode(file_id)
        return decoded.media_id, decoded.access_hash
    except Exception:
        # পুরোনো পদ্ধতির জন্য ফলব্যাক (যদি প্রয়োজন হয়)
        import base64
        from struct import unpack
        try:
            unpacked = unpack("<iiqq", base64.urlsafe_b64decode(file_id + "=" * (-len(file_id) % 4)))
            return unpacked[2], unpacked[3]
        except Exception as e:
            print(f"Error unpacking file_id: {e}")
            return None, None


# --- ফোর্স সাবস্ক্রাইব ডেকরোটর ---
def check_fsub(func):
    """যেকোনো কমান্ড চালানোর আগে ফোর্স সাবস্ক্রাইব চেক করার জন্য ডেকরোটর"""
    async def wrapper(client, message):
        user_id = message.from_user.id
        
        # প্রিমিয়াম ব্যবহারকারী হলে চেক করার দরকার নেই
        # if await db.has_premium_access(user_id):
        #     return await func(client, message)

        public, private = await db.get_fsub_channels()
        if not public and not private: # যদি কোনো চ্যানেল সেট করা না থাকে
            return await func(client, message)

        not_joined_channels = []
        
        # পাবলিক চ্যানেল চেক (সদস্য থাকতেই হবে)
        for channel_id in public:
            try:
                await client.get_chat_member(channel_id, user_id)
            except UserNotParticipant:
                not_joined_channels.append(channel_id)
            except Exception as e:
                print(f"Error checking public channel {channel_id}: {e}")

        # প্রাইভেট চ্যানেল চেক (জয়েন রিকোয়েস্ট পাঠালেই হবে)
        for channel_id in private:
            try:
                await client.get_chat_member(channel_id, user_id)
            except UserNotParticipant:
                if not await db.has_sent_join_request(user_id, channel_id):
                    not_joined_channels.append(channel_id)
            except Exception as e:
                print(f"Error checking private channel {channel_id}: {e}")

        if not_joined_channels:
            buttons = []
            for channel_id in list(set(not_joined_channels)):
                try:
                    chat = await client.get_chat(channel_id)
                    buttons.append([InlineKeyboardButton(f'📢 Join {chat.title}', url=chat.invite_link)])
                except Exception as e:
                    print(f"Error creating join button for {channel_id}: {e}")
            
            buttons.append([InlineKeyboardButton("♻️ Try Again ♻️", url=f"https://t.me/{temp.BOT_USERNAME}?start")])
            
            caption = f"👋 Hello {message.from_user.mention},\n\nবটটি ব্যবহার করতে, আপনাকে নিচের চ্যানেলগুলোতে জয়েন করতে হবে।"
            await message.reply_photo(photo=random.choice(FSUB_PICS), caption=caption, reply_markup=InlineKeyboardMarkup(buttons))
            return

        return await func(client, message)
    return wrapper

# --- ভেরিফিকেশন সিস্টেমের হেল্পার ফাংশন ---
async def get_verify_token(user_id, file_id):
    token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10))
    VERIFY_TOKENS[token] = {'user_id': user_id, 'file_id': file_id, 'timestamp': datetime.datetime.now()}
    return token

async def check_verify_token(token):
    return VERIFY_TOKENS.get(token)

async def mark_user_as_verified(user_id):
    expiry_time = datetime.datetime.now() + datetime.timedelta(hours=VERIFY_EXPIRE)
    await db.update_verify_status(user_id, expiry_time)

async def is_user_verified(user_id):
    if not VERIFY:
        return True
    
    expiry_time = await db.get_verify_status(user_id)
    return expiry_time and datetime.datetime.now() < expiry_time

# --- লিঙ্ক শর্টনার ফাংশন ---
async def get_shortlink(link):
    if not IS_SHORTLINK:
        return link
    
    base_url = f"https://{SHORTLINK_URL}/api"
    params = {'api': SHORTLINK_API, 'url': link}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url, params=params, raise_for_status=True, timeout=5) as response:
                data = await response.json()
                if data.get("status") == "success":
                    return data.get("shortenedUrl")
                else:
                    print(f"Shortener Error: {data.get('message')}")
                    return link
    except Exception as e:
        print(f"Error during link shortening: {e}")
        return link
