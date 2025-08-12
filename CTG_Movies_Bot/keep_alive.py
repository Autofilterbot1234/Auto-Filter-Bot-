import asyncio
import logging
import aiohttp
from info import URL, ON_HEROKU

# লগিং সেটআপ
logger = logging.getLogger(__name__)

# পিং করার ಮಧ್ಯবর্তী সময় (সেকেন্ডে)
PING_INTERVAL = 300  # 5 minutes

async def ping_server():
    """সার্ভারকে পিং করে সচল রাখার ফাংশন"""
    if not ON_HEROKU:
        logger.info("Not on Heroku, skipping keep-alive ping.")
        return

    while True:
        await asyncio.sleep(PING_INTERVAL)
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(URL) as resp:
                    if resp.status == 200:
                        logger.info(f"Keep-alive ping successful (Status: {resp.status})")
                    else:
                        logger.warning(f"Keep-alive ping failed with status: {resp.status}")
        except Exception as e:
            logger.error(f"Keep-alive ping failed: {e}")
