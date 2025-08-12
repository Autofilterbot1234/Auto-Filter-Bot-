import sys
import glob
import logging
import asyncio
import importlib
from pathlib import Path
from pyrogram import Client, idle
from aiohttp import web

from info import LOG_CHANNEL, ON_HEROKU, PORT, URL
from script import script
from CTG_Movies_Bot.bot import CTG_Movies_Bot
from CTG_Movies_Bot.server import web_server
from CTG_Movies_Bot.keep_alive import ping_server
from database.ia_filterdb import MediaModels, mongo_clients, DATABASE_NAME
from utils.temp import temp
from plugins.debugger import raw_update_handler
from pyrogram.handlers import RawUpdateHandler

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s")
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

async def load_plugins():
    """প্লাগইনগুলো সরাসরি লোড এবং হ্যান্ডলার রেজিস্টার করার ফাংশন"""
    plugin_files = glob.glob("plugins/*.py")
    for file_path in plugin_files:
        plugin_name = Path(file_path).stem
        try:
            module = importlib.import_module(f"plugins.{plugin_name}")
            logger.info(f"Successfully Imported: {plugin_name}")
            
            # মডিউলের মধ্যে থাকা Pyrogram হ্যান্ডলারগুলো ক্লায়েন্টে যোগ করা হচ্ছে
            for item in dir(module):
                if item.startswith("handle_"): # Convention: handlers start with handle_
                    handler = getattr(module, item)
                    if callable(handler):
                        CTG_Movies_Bot.add_handler(handler)
                        logger.info(f"Added handler from {plugin_name}: {item}")

        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_name}: {e}", exc_info=True)

async def main():
    logger.info("Initializing Bot...")
    
    # --- সব প্লাগইন এবং হ্যান্ডলার লোড করা হচ্ছে ---
    # await load_plugins() # Pyrogram start করার আগে হ্যান্ডলার লোড করার চেষ্টা

    await CTG_Movies_Bot.start()
    bot_info = await CTG_Movies_Bot.get_me()
    temp.BOT_USERNAME = bot_info.username
    temp.BOT_ID = bot_info.id
    
    CTG_Movies_Bot.add_handler(RawUpdateHandler(raw_update_handler))
    logger.info("Raw update handler for debugging has been added.")
    
    # --- বাকি কাজগুলো অপরিবর্তিত ---
    if ON_HEROKU:
        asyncio.create_task(ping_server())

    # ... (ডাটাবেস স্ট্যাটাস চেক করার কোড) ...
    
    app = web.AppRunner(await web_server())
    await app.setup()
    bind_address = "0.0.0.0"
    await web.TCPSite(app, bind_address, PORT).start()
    
    logger.info(f"{bot_info.first_name} is started.")
    if LOG_CHANNEL:
        await CTG_Movies_Bot.send_message(LOG_CHANNEL, "<b>✅ Bot restarted!</b>")
            
    await idle()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Bot stopped.')
    except Exception as err:
        logger.error(f"Critical error during bot execution: {err}", exc_info=True)
