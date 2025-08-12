import os
import logging
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from info import ADMINS, GRP_LNK, OWNER_LNK, PICS
from Script import script
from database.users_chats_db import db
from database.ia_filterdb import MediaModels
from utils.temp import temp

logger = logging.getLogger(__name__)

@Client.on_message(filters.command("start") & filters.private)
async def start(client, message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
    
    buttons = [
        [InlineKeyboardButton('➕ Add Me To Your Group ➕', url=f'http://t.me/{temp.BOT_USERNAME}?startgroup=true')],
        [InlineKeyboardButton('🤔 About Me', callback_data='about')]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await message.reply_photo(
        photo=random.choice(PICS),
        caption=script.START_TXT.format(mention=message.from_user.mention),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_message(filters.command("start") & filters.group)
async def group_start(client, message):
    if not await db.get_chat(message.chat.id):
        await db.add_chat(message.chat.id, message.chat.title)
    await message.reply_text(script.G_START_TXT)

@Client.on_message(filters.command("stats") & filters.user(ADMINS))
async def stats_command(client, message):
    total_users = await db.total_users_count()
    total_chats = await db.total_chat_count()
    
    total_files = 0
    db_status_text = ""
    for i, model in enumerate(MediaModels):
        count = await model.count_documents({})
        total_files += count
        db_status_text += f"  - <b>Database {i+1}:</b> {count} files\n"
    
    await message.reply_text(
        script.STATUS_TXT.format(
            total_files=total_files,
            total_users=total_users,
            total_chats=total_chats,
            db_status=db_status_text
        ),
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast_command(client, message):
    # এই ফিচারটি পরে আরও উন্নত করা যেতে পারে (যেমন সফল, ব্যর্থ কাউন্ট সহ)
    all_users = await db.get_all_users()
    broadcast_msg = message.reply_to_message
    total_users = await db.total_users_count()
    sts = await message.reply_text(f"Broadcasting to {total_users} users...")

    done = 0
    async for user in all_users:
        try:
            await broadcast_msg.copy(chat_id=int(user['id']))
            done += 1
        except Exception:
            pass # আপাতত ব্যর্থ হলে কিছু করছি না
    await sts.edit_text(f"Broadcast complete! Sent to {done} users.")

@Client.on_callback_query(filters.regex('^about$'))
async def about_callback(client, query):
    bot_info = await client.get_me()
    buttons = [[InlineKeyboardButton('⬅️ Back', callback_data='back_to_start')]]
    
    await query.message.edit_caption(
        caption=script.ABOUT_TXT.format(
            bot_name=bot_info.mention,
            owner_link=OWNER_LNK
        ),
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex('^back_to_start$'))
async def back_to_start_callback(client, query):
    buttons = [
        [InlineKeyboardButton('➕ Add Me To Your Group ➕', url=f'http://t.me/{temp.BOT_USERNAME}?startgroup=true')],
        [InlineKeyboardButton('🤔 About Me', callback_data='about')]
    ]
    await query.message.edit_caption(
        caption=script.START_TXT.format(mention=query.from_user.mention),
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )
