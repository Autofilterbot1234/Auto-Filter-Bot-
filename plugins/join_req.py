from pyrogram import Client, filters
from pyrogram.types import ChatJoinRequest
from database.users_chats_db import db

# এই হ্যান্ডলারটি শুধুমাত্র অ্যাডমিন কর্তৃক সেট করা প্রাইভেট চ্যানেলগুলোতে কাজ করবে
@Client.on_chat_join_request()
async def handle_join_request(client, join_request: ChatJoinRequest):
    # ডাটাবেস থেকে প্রাইভেট চ্যানেলের তালিকা আনা হচ্ছে
    _, private_channels = await db.get_fsub_channels()

    if join_request.chat.id in private_channels:
        user_id = join_request.from_user.id
        channel_id = join_request.chat.id
        
        await db.add_join_request(user_id, channel_id)
        print(f"User {user_id} sent a join request to private channel {channel_id}. Saved to DB.")
        
        # আপনি চাইলে রিকোয়েস্টটি অটো-অ্যাপ্রুভ করতে পারেন
        # try:
        #     await client.approve_chat_join_request(chat_id=channel_id, user_id=user_id)
        # except Exception as e:
        #     print(f"Could not approve join request: {e}")
