import logging
import asyncio
from pyrogram import idle
from aiohttp import web

# --- কোর মডিউল ইম্পোর্ট ---
from info import LOG_CHANNEL, ON_HEROKU, PORT, URL
from CTG_Movies_Bot.bot import CTG_Movies_Bot
from CTG_Movies_Bot.server import web_server
from CTG_Movies_Bot.keep_alive import ping_server
from utils.temp import temp

# --- সব প্লাগইন ম্যানুয়ালি ইম্পোর্ট করা হচ্ছে ---
# এটি নিশ্চিত করবে যে প্রতিটি হ্যান্ডলার সঠিকভাবে রেজিস্টার হয়েছে
try:
    from plugins import commands
    from plugins import channel_indexer
    from plugins import db_admin
    from plugins import fsub_admin
    from plugins import join_req
    from plugins import pm_filter
    from plugins import stream
    from plugins import user_index
    from plugins import debugger
    print("All plugins imported successfully.")
except ImportError as e:
    print(f"Error importing plugins: {e}")
    # কোনো প্লাগইন না চললে বট বন্ধ হয়ে যাবে, যা error ধরতে সাহায্য করবে
    exit()

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
    
    if ON_HEROKU:
        asyncio.create_task(ping_server())

    app = web.AppRunner(await web_server())
    await app.setup()
    bind_address = "0.0.0.0"
    await web.TCPSite(app, bind_address, PORT).start()
    
    logger.info(f"{bot_info.first_name} is started.")
    if LOG_CHANNEL:
        try:
            await CTG_Movies_Bot.send_message(LOG_CHANNEL, "<b>✅ Bot restarted and online!</b>")
        except Exception as e:
            logger.warning(f"Could not send start message to log channel: {e}")
            
    await idle()
    await CTG_Movies_Bot.stop()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Bot stopped.')
