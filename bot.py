import sys
import glob
import logging
import asyncio
import importlib
from pathlib import Path
from pyrogram import Client, idle
from aiohttp import web
from pyrogram.handlers import RawUpdateHandler

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
from plugins.debugger import raw_update_handler

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
    
    CTG_Movies_Bot.add_handler(RawUpdateHandler(raw_update_handler))
    logger.info("Raw update handler for debugging has been added.")
    
    if ON_HEROKU:
        asyncio.create_task(ping_server())

    # ... (ডাটাবেস স্ট্যাটাস চেক করার কোড অপরিবর্তিত) ...
    total_files = 0
    for i, model in enumerate(MediaModels):
        try:
            count = await model.count_documents({})
            total_files += count
            logger.info(f"Database {i+1}: Contains {count} files.")
        except Exception as e:
            logger.error(f"Could not get stats for Database {i+1}: {e}")
    logger.info(f"Total files in all databases: {total_files}")
    
    app = web.AppRunner(await web_server())
    await app.setup()
    bind_address = "0.0.0.0"
    await web.TCPSite(app, bind_address, PORT).start()
    
    logger.info(f"{bot_info.first_name} is started.")
    
    # ----- প্রধান পরিবর্তনটি এখানে করা হয়েছে -----
    if LOG_CHANNEL:
        try:
            await CTG_Movies_Bot.send_message(LOG_CHANNEL, "<b>✅ Bot has been restarted successfully!</b>")
        except Exception as e:
            # যদি Peer id invalid error আসে, তাহলে বট ক্র্যাশ না করে একটি warning দেখাবে
            logger.warning(f"Could not send start message to log channel ({LOG_CHANNEL}): {e}")
            logger.warning("This is a common cold start issue. Bot will still function correctly.")
            
    await idle()
    await CTG_Movies_Bot.stop()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Bot stopped.')
