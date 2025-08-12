import logging
import math
import mimetypes
import asyncio
from pyrogram import Client, filters
from aiohttp import web
from jinja2 import Environment, FileSystemLoader

from CTG_Movies_Bot.server import routes
from CTG_Movies_Bot.bot import Bot as CTG_Movies_Bot
from info import URL, PROTECT_CONTENT, DELETE_TIME, FQDN
from database.ia_filterdb import get_file_details
from utils.helpers import check_verify_token, mark_user_as_verified, get_size
from utils.temp import temp

logger = logging.getLogger(__name__)

# Jinja2 টেমপ্লেট এনভায়রনমেন্ট সেটআপ
template_env = Environment(loader=FileSystemLoader('CTG_Movies_Bot/template'))

# --- ওয়েব রুট হ্যান্ডলারগুলো ---

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
    
    redirect_url = f"https://t.me/{temp.BOT_USERNAME}?start=file_{file_id}"
    return web.HTTPFound(redirect_url)


@routes.get(r"/watch/{media_id:\d+}/{file_name}")
async def stream_page_handler(request: web.Request):
    try:
        media_id = int(request.match_info['media_id'])
        file_details = await get_file_details(str(media_id))
        if not file_details:
            return web.HTTPNotFound(text="File not found")

        file_info = file_details[0]
        template = template_env.get_template('stream.html')
        
        page_content = template.render(
            file_name=file_info.file_name,
            file_size=get_size(file_info.file_size),
            stream_link=f"{URL}stream/{media_id}/{file_info.file_name.replace(' ', '_')}",
            download_link=f"{URL}download/{media_id}/{file_info.file_name.replace(' ', '_')}"
        )
        return web.Response(text=page_content, content_type='text/html')
    except Exception as e:
        logger.error(f"Error rendering stream page: {e}", exc_info=True)
        return web.HTTPInternalServerError()


@routes.get(r"/(stream|download)/{media_id:\d+}/{file_name}")
async def stream_and_download_handler(request: web.Request):
    try:
        media_id = int(request.match_info['media_id'])
        return await media_streamer(request, media_id)
    except Exception as e:
        logger.error(f"Error in stream/download handler: {e}", exc_info=True)
        return web.HTTPInternalServerError()


# --- স্ট্রিমিং এর মূল লজিক (media_streamer) ---
async def media_streamer(request: web.Request, media_id: int):
    range_header = request.headers.get("Range", 0)
    
    file_details = await get_file_details(str(media_id))
    if not file_details:
        raise web.HTTPNotFound(text="File not found in database.")
    
    stream_client = CTG_Movies_Bot.get_instance()
    if not stream_client:
        raise web.HTTPInternalServerError(text="Bot client not available.")
        
    file_info = file_details[0]
    file_size = file_info.file_size

    from_bytes, until_bytes = 0, file_size - 1
    if range_header:
        try:
            from_bytes_str, until_bytes_str = range_header.replace("bytes=", "").split("-")
            from_bytes = int(from_bytes_str) if from_bytes_str else 0
            until_bytes = int(until_bytes_str) if until_bytes_str else file_size - 1
        except ValueError:
            return web.Response(status=400, text="Invalid Range Header")

    req_length = until_bytes - from_bytes + 1
    
    mime_type = mimetypes.guess_type(file_info.file_name)[0] or "application/octet-stream"
    headers = {
        "Content-Type": mime_type,
        "Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
        "Content-Length": str(req_length),
        "Accept-Ranges": "bytes",
        "Content-Disposition": f'attachment; filename="{file_info.file_name}"'
    }

    response = web.StreamResponse(status=206 if range_header else 200, headers=headers)
    await response.prepare(request)

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
        
        stream_link = f"{URL}watch/{file_info.id}/{file_info.file_name.replace(' ', '_')}"
        download_link = f"{URL}download/{file_info.id}/{file_info.file_name.replace(' ', '_')}"

        buttons = [
            [InlineKeyboardButton("🖥️ Watch Online 🖥️", url=stream_link)],
            [InlineKeyboardButton("📥 Direct Download 📥", url=download_link)]
        ]
        
        try:
            msg = await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=file_id,
                caption=f"**File:** `{file_info.file_name}`\n**Size:** `{get_size(file_info.file_size)}`",
                protect_content=PROTECT_CONTENT,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            if AUTO_DELETE:
                await asyncio.sleep(DELETE_TIME)
                await msg.delete()
        except Exception as e:
            await message.reply_text("ফাইলটি পাঠানো সম্ভব হচ্ছে না। অনুগ্রহ করে বটকে আবার স্টার্ট করুন।")
            logger.error(f"Error sending file to user: {e}")
