import sys
import glob
import logging
import asyncio
import importlib
from pathlib import Path
from pyrogram import Client, idle
from aiohttp import web
from pyrogram.handlers import RawUpdateHandler # <-- ডিবাগারের জন্য নতুন ইম্পোর্ট

# --- তথ্য ও স্ক্রিপ্ট ইম্পোর্ট ---
from info import (
    LOG_CHANNEL, ON_HEROKU, PORT, URL
)
from script import script

# --- কাস্টম মডিউল ইম্পোর্ট ---
from CTG_Movies_Bot.bot import CTG_Movies_Bot
from CTG_Movies_Bot.server import web_server
from CTG_Movies_Bot.keep_alive import ping_server
from database.ia_filterdb import MediaModels, mongo_clients, DATABASE_NAME
from utils.temp import temp
from plugins.debugger import raw_update_handler # <-- ডিবাগার ফাংশন ইম্পোর্ট

# --- লগিং সেটআপ ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# --- মূল ফাংশন ---
async def main():
    logger.info("Initializing Bot...")
    
    await CTG_Movies_Bot.start()
    bot_info = await CTG_Movies_Bot.get_me()
    temp.BOT_USERNAME = bot_info.username
    temp.BOT_ID = bot_info.id
    
    # ----- ডিবাগিং হ্যান্ডলারটি এখানে যোগ করা হয়েছে -----
    CTG_Movies_Bot.add_handler(RawUpdateHandler(raw_update_handler))
    logger.info("Raw update handler for debugging has been added.")
    
    # --- ওয়েব সার্ভার এবং অন্যান্য কাজ ---
    if ON_HEROKU:
        asyncio.create_task(ping_server())

    # ... (ডাটাবেস স্ট্যাটাস চেক করার কোড) ...
    
    app = web.AppRunner(await web_server())
    await app.setup()
    bind_address = "0.0.0.0"
    await web.TCPSite(app, bind_address, PORT).start()
    
    logger.info(f"{bot_info.first_name} is started.")
    if LOG_CHANNEL:
        try:
            await CTG_Movies_Bot.send_message(LOG_CHANNEL, "<b>✅ Bot restarted with debugger!</b>")
        except Exception as e:
            logger.warning(f"Could not send start message to log channel: {e}")
            
    await idle()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Bot stopped.')
