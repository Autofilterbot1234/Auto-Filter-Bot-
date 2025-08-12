import logging
from pyrogram import Client
from info import API_ID, API_HASH, BOT_TOKEN

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

_client_instance = None

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="CTG_Movies_Bot_InMemory",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=20,
            in_memory=True
            # plugins={"root": "plugins"} <-- এই লাইনটি সরিয়ে দেওয়া হয়েছে
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
        return _client_instance

CTG_Movies_Bot = Bot()
