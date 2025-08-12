import logging
from pyrogram import Client
from info import API_ID, API_HASH, BOT_TOKEN, SESSION

# লগিং সেটআপ
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# একটি গ্লোবাল ভেরিয়েবল ক্লায়েন্টের ইনস্ট্যান্স রাখার জন্য
_client_instance = None

class Bot(Client):
    """আপনার কাস্টম বট ক্লাস"""
    def __init__(self):
        super().__init__(
            name=SESSION,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=20,
            plugins={"root": "plugins"},
            sleep_threshold=10,
        )
        logger.info("Bot class initialized.")

    async def start(self):
        global _client_instance
        await super().start()
        me = await self.get_me()
        _client_instance = self
        logger.info(f"{me.first_name} | @{me.username} started.")

    async def stop(self, *args):
        global _client_instance
        await super().stop()
        _client_instance = None
        logger.info("Bot stopped.")

    @staticmethod
    def get_instance():
        """অন্যান্য মডিউল থেকে ক্লায়েন্টের অ্যাক্টিভ ইনস্ট্যান্স পাওয়ার জন্য"""
        return _client_instance

# ক্লাসের একটি ইনস্ট্যান্স তৈরি করা হচ্ছে যা অন্য ফাইল থেকে ইম্পোর্ট করা হবে
CTG_Movies_Bot = Bot()
