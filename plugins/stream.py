import logging
import math
import mimetypes
from pyrogram import Client
from aiohttp import web
from CTG_Movies_Bot.server import routes  # সার্ভার থেকে রুট ইম্পোর্ট করা হচ্ছে
from info import URL, PROTECT_CONTENT, DELETE_TIME
from database.ia_filterdb import get_file_details
from utils.helpers import check_verify_token, mark_user_as_verified
from utils.temp import temp

logger = logging.getLogger(__name__)

# --- ভেরিফিকেশন রুট হ্যান্ডলার ---
@routes.get("/verify")
async def verify_handler(request: web.Request):
    token = request.query.get("token")
    if not token:
        return web.HTTPNotFound(text="Missing token.")

    token_info = await check_verify_token(token)
    if not token_info:
        return web.HTTPForbidden(text="Link expired or invalid.")

    user_id = token_info['user_id']
    file_id = token_info['file_id']
    
    await mark_user_as_verified(user_id)
    
    # ব্যবহারকারীকে টেলিগ্রামে ফাইলের লিঙ্কে রিডাইরেক্ট করা হচ্ছে
    redirect_url = f"https://t.me/{temp.BOT_USERNAME}?start=file_{file_id}"
    return web.HTTPFound(redirect_url)


# --- স্ট্রিমিং এর মূল লজিক (media_streamer) ---
async def media_streamer(request: web.Request, media_id: int):
    range_header = request.headers.get("Range", 0)
    
    file_details = await get_file_details(str(media_id))
    if not file_details:
        raise web.HTTPNotFound(text="File not found in database.")
    
    stream_client = Client.get_instance() # বট ক্লায়েন্টের ইনস্ট্যান্স নেওয়া হচ্ছে
    file_info = file_details[0]
    file_size = file_info.file_size

    from_bytes, until_bytes = 0, file_size - 1
    if range_header:
        try:
            from_bytes, until_bytes = [int(x) for x in range_header.replace("bytes=", "").split("-")]
        except ValueError:
            pass # ভুল রেঞ্জ হেডার উপেক্ষা করা হচ্ছে

    req_length = until_bytes - from_bytes + 1

    # --- HTTP Headers সেট করা হচ্ছে ---
    mime_type = mimetypes.guess_type(file_info.file_name)[0] or "application/octet-stream"
    headers = {
        "Content-Type": mime_type,
        "Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
        "Content-Length": str(req_length),
        "Accept-Ranges": "bytes",
        "Content-Disposition": f'attachment; filename="{file_info.file_name}"'
    }

    # --- স্ট্রিমিং শুরু করা হচ্ছে ---
    response = web.StreamResponse(status=206 if range_header else 200, headers=headers)
    await response.prepare(request)

    # Pyrogram থেকে ফাইল চাঙ্ক (chunk) ডাউনলোড এবং ক্লায়েন্টকে পাঠানো হচ্ছে
    async for chunk in stream_client.iter_download(media_id, offset=from_bytes):
        try:
            await response.write(chunk)
        except Exception as e:
            logger.warning(f"Connection lost during streaming: {e}")
            break
            
    return response

# --- /start কমান্ডের ফাইল হ্যান্ডলার ---
@Client.on_message(filters.private & filters.command("start"))
async def start_file_handler(client, message):
    if len(message.command) > 1 and message.command[1].startswith("file_"):
        file_id = message.command[1].split("_", 1)[1]
        
        file_details = await get_file_details(file_id)
        if not file_details:
            return await message.reply("404: File not found.")
            
        file_info = file_details[0]
        
        msg = await client.send_cached_media(
            chat_id=message.from_user.id,
            file_id=file_id,
            caption=f"**{file_info.file_name}**",
            protect_content=PROTECT_CONTENT
        )

        if AUTO_DELETE:
            await asyncio.sleep(DELETE_TIME)
            await msg.delete()
