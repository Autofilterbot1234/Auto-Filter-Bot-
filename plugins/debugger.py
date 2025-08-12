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
@Client.on_message(filters.command("ping") & filters.private)
async def ping_command(client, message):
    """
    বটটি মেসেজ প্রসেস করতে পারছে কিনা তা পরীক্ষা করার জন্য একটি সাধারণ কমান্ড।
    """
    logger.info(f"Received /ping command from user {message.from_user.id}")
    try:
        await message.reply_text("Pong!")
        logger.info("Successfully replied 'Pong!'")
    except Exception as e:
        logger.error(f"Failed to reply to /ping command: {e}")
