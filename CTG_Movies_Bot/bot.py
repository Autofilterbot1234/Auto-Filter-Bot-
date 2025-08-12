import logging
from pyrogram import Client
from info import API_ID, API_HASH, BOT_TOKEN, SESSION

# লগিং সেটআপ
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class Bot(Client):
    """আপনার কাস্টম বট ক্লাস"""
    def __init__(self):
        super().__init__(
            name=SESSION,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=20,  # একই সাথে কতগুলো কাজ করতে পারবে তার সংখ্যা
            plugins={"root": "plugins"},
            sleep_threshold=10,
        )
        logger.info("Bot class initialized.")

    async def start(self):
        await super().start()
        me = await self.get_me()
        logger.info(f"{me.first_name} | @{me.username} started.")

    async def stop(self, *args):
        await super().stop()
        logger.info("Bot stopped.")

# ক্লাসের একটি ইনস্ট্যান্স তৈরি করা হচ্ছে যা অন্য ফাইল থেকে ইম্পোর্ট করা হবে
CTG_Movies_Bot = Bot()
