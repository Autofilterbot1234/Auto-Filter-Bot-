from pyrogram import Client, filters, enums
from info import CHANNELS
from database.ia_filterdb import save_file

# শুধুমাত্র ডকুমেন্ট, ভিডিও এবং অডিও ফাইল ফিল্টার করা হচ্ছে
media_filter = filters.document | filters.video | filters.audio

@Client.on_message(filters.chat(CHANNELS) & media_filter & ~filters.edited)
async def channel_media_handler(client, message):
    """চ্যানেল থেকে আসা মিডিয়া ফাইল হ্যান্ডেল এবং সেভ করে"""
    media = message.document or message.video or message.audio
    if not media:
        return

    # ফাইলের কিছু প্রয়োজনীয় তথ্য যোগ করা হচ্ছে
    media.file_type = message.media.value
    media.caption = message.caption
    
    # ফাইলটি ডাটাবেসে সেভ করা হচ্ছে
    saved, status_code = await save_file(media)
    
    if saved:
        print(f"Successfully saved file: {media.file_name}")
