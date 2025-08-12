import logging
import asyncio
import re
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, ChannelInvalid, ChatAdminRequired, UsernameInvalid
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from info import ADMINS, LOG_CHANNEL
from database.ia_filterdb import save_file
from utils.temp import temp

logger = logging.getLogger(__name__)
lock = asyncio.Lock()

@Client.on_message(filters.forwarded & filters.private & filters.incoming)
async def handle_forwarded_message(client, message):
    """ব্যবহারকারীদের ফরোয়ার্ড করা মেসেজ থেকে ইনডেক্স রিকোয়েস্ট হ্যান্ডেল করে"""
    if message.forward_from_chat and message.forward_from_chat.type == enums.ChatType.CHANNEL:
        last_msg_id = message.forward_from_message_id
        chat_id = message.forward_from_chat.username or message.forward_from_chat.id
        await process_index_request(client, message, chat_id, last_msg_id)

@Client.on_message(filters.regex(r"(https?://t\.me/|https?://telegram\.me/|https?://telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)") & filters.private)
async def handle_link_message(client, message):
    """ব্যবহারকারীদের পাঠানো লিঙ্ক থেকে ইনডেক্স রিকোয়েস্ট হ্যান্ডেল করে"""
    match = re.match(r"(https?://t\.me/|https?://telegram\.me/|https?://telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)", message.text)
    if match:
        chat_id = match.group(3)
        last_msg_id = int(match.group(4))
        if chat_id.isnumeric():
            chat_id = int("-100" + chat_id)
        await process_index_request(client, message, chat_id, last_msg_id)

async def process_index_request(client, message, chat_id, last_msg_id):
    """ইনডেক্স রিকোয়েস্ট প্রসেস করার মূল ফাংশন"""
    try:
        await client.get_chat(chat_id)
    except (ChannelInvalid, UsernameInvalid) as e:
        return await message.reply(f"চ্যানেলটি খুঁজে পাওয়া যায়নি: {e}")
    except Exception as e:
        return await message.reply(f"একটি সমস্যা হয়েছে: {e}")

    buttons = [
        [
            InlineKeyboardButton('✅ Accept', callback_data=f'index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}'),
            InlineKeyboardButton('❌ Reject', callback_data=f'index#reject#{message.from_user.id}')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await client.send_message(
        LOG_CHANNEL,
        f"**#IndexRequest**\n\n"
        f"**From:** {message.from_user.mention} (`{message.from_user.id}`)\n"
        f"**Chat:** `{chat_id}`\n"
        f"**Last Message ID:** `{last_msg_id}`",
        reply_markup=reply_markup
    )
    await message.reply('✅ আপনার অনুরোধটি পর্যালোচনার জন্য পাঠানো হয়েছে। অ্যাডমিনরা গ্রহণ করলে আপনাকে জানানো হবে।')


@Client.on_callback_query(filters.regex(r'^index#'))
async def index_callback_handler(client, query):
    if query.from_user.id not in ADMINS:
        return await query.answer("This is not for you!", show_alert=True)

    action, chat_id, last_msg_id, user_id = query.data.split('#', 3)
    user_id = int(user_id)

    if action == 'reject':
        await query.message.delete()
        await client.send_message(user_id, 'দুঃখিত, আপনার চ্যানেল ইনডেক্স করার অনুরোধটি প্রত্যাখ্যান করা হয়েছে।')
        return await query.answer("Request Rejected.")

    if lock.locked():
        return await query.answer("আরেকটি ইনডেক্সিং প্রক্রিয়া চলছে। অনুগ্রহ করে অপেক্ষা করুন।", show_alert=True)
    
    await query.answer("Processing...")
    await query.message.edit_reply_markup(None) # বাটনগুলো সরিয়ে দেওয়া হচ্ছে

    msg = await query.message.edit_text(
        "ইনডেক্সিং শুরু হচ্ছে... এটি অনেক সময় নিতে পারে।",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Cancel', callback_data='index_cancel')]])
    )
    
    temp.CANCEL_INDEXING = False
    total_files, skipped, failed = 0, 0, 0
    
    async with lock:
        try:
            current = 0
            async for message in client.iter_messages(chat_id, reverse=True, offset_id=int(last_msg_id)):
                if temp.CANCEL_INDEXING:
                    break
                current += 1
                if current % 100 == 0:
                    await msg.edit_text(f"ইনডেক্সিং চলছে...\nTotal: {total_files} | Skipped: {skipped} | Failed: {failed}")

                if message.media:
                    media = message.document or message.video or message.audio
                    if not media:
                        continue
                    
                    media.file_type = message.media.value
                    media.caption = message.caption
                    
                    saved, code = await save_file(media)
                    if saved:
                        total_files += 1
                    elif code == 0:
                        skipped += 1
                    else:
                        failed += 1
        except Exception as e:
            logger.error(f"Indexing failed: {e}")
            await msg.edit_text(f"একটি সমস্যা হয়েছে: {e}")
        finally:
            await msg.edit_text(f"✅ ইনডেক্সিং সম্পন্ন!\n\n**Total Files Indexed:** {total_files}\n**Duplicate Files Skipped:** {skipped}\n**Failed to Save:** {failed}")
            await client.send_message(user_id, f"আপনার চ্যানেল (`{chat_id}`) সফলভাবে ইনডেক্স করা হয়েছে।")
            temp.CANCEL_INDEXING = False

@Client.on_callback_query(filters.regex(r'^index_cancel$'))
async def cancel_indexing_handler(client, query):
    if query.from_user.id not in ADMINS:
        return await query.answer("This is not for you!", show_alert=True)
    
    temp.CANCEL_INDEXING = True
    await query.answer("Cancelling indexing process...")
