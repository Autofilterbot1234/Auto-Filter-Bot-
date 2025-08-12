from pyrogram import Client, filters, enums
from info import CHANNELS
from database.ia_filterdb import save_file

# শুধুমাত্র ডকুমেন্ট, ভিডিও এবং অডিও ফাইল ফিল্টার করা হচ্ছে
media_filter = filters.document | filters.video | filters.audio

# --- প্রধান পরিবর্তন: ~filters.edited_message ফিল্টারটি সরিয়ে দেওয়া হয়েছে ---
@Client.on_message(filters.chat(CHANNELS) & media_filter)
async def channel_media_handler(client, message):
    """চ্যানেল থেকে আসা মিডিয়া ফাইল হ্যান্ডেল এবং সেভ করে"""
    
    # যদি মেসেজটি এডিট করা হয়, তাহলে এটিকে উপেক্ষা করা হবে
    if message.edit_date:
        return

    media = message.document or message.video or message.audio
    if not media:
        return

    media.file_type = message.media.value
    media.caption = message.caption
    
    saved, status_code = await save_file(media)
    
    if saved:
        print(f"Successfully saved file: {media.file_name}")
