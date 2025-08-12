import logging
from pyrogram import Client, filters
from pyrogram.handlers import RawUpdateHandler

# লগিং সেটআপ
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# --- Raw Update Handler ---
# এই ফাংশনটি টেলিগ্রাম থেকে আসা প্রতিটি আপডেট লগ করবে
async def raw_update_handler(client, update, users, chats):
    """
    এটি একটি বিশেষ ডিবাগিং টুল যা টেলিগ্রাম থেকে আসা *প্রতিটি* আপডেট
    (মেসেজ, বাটন ক্লিক ইত্যাদি) লগ করবে, কোনো ফিল্টার ছাড়াই।
    """
    logger.info(f"--- RAW UPDATE RECEIVED ---\n{update}\n---------------------------")

# --- একটি সাধারণ পিং কমান্ড ---
@Client.on_message(filters.command("ping"))
async def ping_command(client, message):
    """
    বটটি মেসেজ প্রসেস করতে পারছে কিনা তা পরীক্ষা করার জন্য একটি সাধারণ কমান্ড।
    """
    logger.info(f"Received /ping command from {message.from_user.id}")
    await message.reply_text("Pong!")

# --- হ্যান্ডলারগুলো যোগ করা হচ্ছে ---
# RawUpdateHandler সরাসরি ক্লায়েন্টে যোগ করতে হয়, তাই আমরা এটি __main__ এ করব।
# আপাতত, এই ফাইলটি শুধু পিং কমান্ডের জন্য থাকবে এবং আমরা বট চালু হওয়ার সময় raw handler যোগ করব।

# bot.py ফাইলে এই হ্যান্ডলারটি যোগ করতে হবে
# CTG_Movies_Bot.add_handler(RawUpdateHandler(raw_update_handler))
