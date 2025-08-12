import asyncio
import re
import math
import random
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from info import ADMINS, IMDB, PROTECT_CONTENT, AUTO_DELETE, DELETE_TIME, GRP_LNK, OWNER_LNK, URL
from script import script # <-- সমস্যাটি এখানে ঠিক করা হয়েছে
from database.ia_filterdb import get_search_results, get_file_details
from utils.helpers import check_fsub, get_size, is_user_verified, get_verify_token, get_shortlink, HOW_TO_VERIFY, TUTORIAL
from utils.temp import temp

# --- ফিল্টার হ্যান্ডলার ---
@Client.on_message(filters.text & (filters.group | filters.private) & ~filters.command(["start", "stats", "broadcast", "addfsub", "delfsub", "fsublist", "delete", "deleteall"]))
@check_fsub
async def auto_filter_handler(client, message):
    query = message.text
    search = re.sub(r'(_|\-|\.|\+|\(|\))', ' ', query).strip()
    
    if len(search) < 2:
        return

    files, next_offset, total_results = await get_search_results(query=search, max_results=5)
    
    if not files:
        return

    if not await is_user_verified(message.from_user.id):
        token = await get_verify_token(message.from_user.id, files[0].file_id)
        verify_link = f"{URL}verify?token={token}"
        short_verify_link = await get_shortlink(verify_link)

        buttons = [
            [InlineKeyboardButton("✅ Click Here to Verify ✅", url=short_verify_link)],
            [InlineKeyboardButton("💡 How to Verify 💡", url=HOW_TO_VERIFY)]
        ]
        await message.reply_text("ফাইলটি পেতে, অনুগ্রহ করে ভেরিফাই করুন।", reply_markup=InlineKeyboardMarkup(buttons))
        return

    buttons = []
    for file in files:
        file_id = file.file_id
        file_name = file.file_name
        buttons.append([
            InlineKeyboardButton(
                text=f"📂 {file_name} [{get_size(file.file_size)}]",
                callback_data=f"file#{file_id}"
            )
        ])
    
    if next_offset:
        buttons.append([
            InlineKeyboardButton("Next ➡️", callback_data=f"next#{search.replace(' ', '_')}#{next_offset}")
        ])

    caption = f"আপনার '{query}' এর জন্য {total_results} টি ফলাফল পাওয়া গেছে।"
    if IMDB:
        # IMDB ফিচার পরে যুক্ত করা হবে
        pass
        
    await message.reply_text(caption, reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex(r'^file#'))
async def file_callback_handler(client, query):
    _, file_id = query.data.split("#")
    
    file_details = await get_file_details(file_id)
    if not file_details:
        return await query.answer("ফাইলটি খুঁজে পাওয়া যায়নি।")
    
    file_info = file_details[0]
    
    main_link = f"https://t.me/{temp.BOT_USERNAME}?start=file_{file_id}"
    download_link = await get_shortlink(main_link)
    
    buttons = [
        [InlineKeyboardButton("📥 Download Now 📥", url=download_link)],
        [InlineKeyboardButton("💡 How to Download 💡", url=TUTORIAL)]
    ]
    
    await query.answer("ফাইলটি আপনার প্রাইভেট মেসেজে পাঠানো হচ্ছে...", show_alert=True)
    
    try:
        msg = await client.send_cached_media(
            chat_id=query.from_user.id,
            file_id=file_id,
            caption=f"**{file_info.file_name}**",
            protect_content=PROTECT_CONTENT,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        if AUTO_DELETE:
            await asyncio.sleep(DELETE_TIME)
            await msg.delete()
    except Exception as e:
        await query.answer(f"ফাইলটি পাঠানো সম্ভব হচ্ছে না। অনুগ্রহ করে বটকে স্টার্ট করুন। Error: {e}", show_alert=True)

@Client.on_callback_query(filters.regex(r'^next#'))
async def next_page_handler(client, query):
    _, query_text, offset = query.data.split("#")
    query_text = query_text.replace('_', ' ')
    offset = int(offset)

    files, next_offset, total_results = await get_search_results(query=query_text, max_results=5, offset=offset)
    if not files:
        return await query.answer("আর কোনো ফাইল নেই।")

    buttons = []
    for file in files:
        buttons.append([
            InlineKeyboardButton(
                text=f"📂 {file.file_name} [{get_size(file.file_size)}]",
                callback_data=f"file#{file.file_id}"
            )
        ])

    current_page = (offset // 5) + 1
    total_pages = math.ceil(total_results / 5)
    
    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(InlineKeyboardButton("⬅️ Back", callback_data=f"next#{query_text.replace(' ', '_')}#{offset - 5}"))
    
    nav_buttons.append(InlineKeyboardButton(f"Page {current_page}/{total_pages}", callback_data="noop"))
    
    if next_offset:
        nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"next#{query_text.replace(' ', '_')}#{next_offset}"))
    
    buttons.append(nav_buttons)

    await query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex(r'^noop$'))
async def noop_callback(client, query):
    await query.answer()
