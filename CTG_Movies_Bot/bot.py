import logging
from pyrogram import Client
from info import API_ID, API_HASH, BOT_TOKEN

# ... (অন্যান্য কোড অপরিবর্তিত)

class Bot(Client):
    """আপনার কাস্টম বট ক্লাস"""
    def __init__(self):
        # ----- প্রধান পরিবর্তনটি এখানে -----
        super().__init__(
            name="CTG_Movies_Bot_InMemory", # একটি নতুন এবং ইউনিক নাম
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=20,
            plugins={"root": "plugins"},
            in_memory=True # <-- এই লাইনটি সেশন ফাইল তৈরি করা বন্ধ করবে
        )
        logger.info("Bot class initialized in in-memory mode.")
    
    # ... (start, stop, get_instance ফাংশনগুলো অপরিবর্তিত থাকবে)

CTG_Movies_Bot = Bot()
