import sys
import glob
import logging
import asyncio
import importlib
from pathlib import Path
from pyrogram import idle
from aiohttp import web

# --- তথ্য ও স্ক্রিপ্ট ইম্পোর্ট ---
from info import (
    BOT_TOKEN, API_ID, API_HASH, SESSION,
    LOG_CHANNEL, ON_HEROKU, PORT, URL, FQDN
)
from Script import script  # নিশ্চিত হও Script ফোল্ডার এবং script.py ফাইল আছে

# --- কাস্টম মডিউল ইম্পোর্ট ---
from CTG_Movies_Bot.bot import CTG_Movies_Bot
from CTG_Movies_Bot.server import web_server
from CTG_Movies_Bot.keep_alive import ping_server
from database.ia_filterdb import MediaModels, mongo_clients, DATABASE_NAME
from utils import temp

# --- লগিং সেটআপ ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# --- প্লাগইন লোড করার জন্য পাথ ---
PLUGIN_PATH = "plugins/*.py"
plugin_files = glob.glob(PLUGIN_PATH)

# --- মূল ফাংশন ---
async def main():
    logger.info("Initializing Bot...")
    
    # --- বট ক্লায়েন্ট শুরু করা হচ্ছে ---
    await CTG_Movies_Bot.start()
    bot_info = await CTG_Movies_Bot.get_me()
    temp.BOT_USERNAME = bot_info.username
    temp.BOT_ID = bot_info.id
    
    # --- সব প্লাগইন ইম্পোর্ট করা হচ্ছে ---
    for filepath in plugin_files:
        plugin_name = Path(filepath).stem
        try:
            spec = importlib.util.spec_from_file_location(f"plugins.{plugin_name}", filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            sys.modules[f"plugins.{plugin_name}"] = module
            logger.info(f"Successfully Imported plugin: {plugin_name}")
        except Exception as e:
            logger.error(f"Failed to import plugin {plugin_name}: {e}")

    # --- Heroku-এর জন্য Keep-Alive ---
    if ON_HEROKU:
        asyncio.create_task(ping_server())

    # --- ডাটাবেস স্ট্যাটাস চেক করা ---
    total_files = 0
    for i, model in enumerate(MediaModels):
        try:
            count = await model.count_documents({})
            total_files += count
            stats = await mongo_clients[i][DATABASE_NAME].command('dbStats')
            size_mb = (stats.get('dataSize', 0) + stats.get('indexSize', 0)) / (1024 * 1024)
            logger.info(f"Database {i+1}: {count} files | Size: {size_mb:.2f} MB")
        except Exception as e:
            logger.error(f"Could not get stats for Database {i+1}: {e}")
    logger.info(f"Total files in all databases: {total_files}")
    
    # --- ওয়েব সার্ভার চালু করা হচ্ছে ---
    app = web.AppRunner(await web_server())
    await app.setup()
    bind_addr = "0.0.0.0" if ON_HEROKU else FQDN
    site = web.TCPSite(app, bind_addr, PORT)
    await site.start()
    logger.info(f"Web server started on {URL}")
    
    # --- বট চালু থাকার বার্তা ---
    logger.info(f"{bot_info.first_name} is started. Bot username: @{bot_info.username}")
    if LOG_CHANNEL:
        try:
            await CTG_Movies_Bot.send_message(LOG_CHANNEL, "<b>✅ Bot is restarted!</b>")
        except Exception as e:
            logger.warning(f"Could not send start message to log channel: {e}")
            
    await idle()

# --- বট চালানো হচ্ছে ---
if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        logger.info('Bot stopped manually.')
    except Exception as err:
        logger.error(f"Error during bot startup: {err}", exc_info=True)
