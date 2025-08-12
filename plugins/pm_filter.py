import asyncio
import re
import math
import random
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from info import ADMINS, IMDB, PROTECT_CONTENT, AUTO_DELETE, DELETE_TIME, GRP_LNK, OWNER_LNK
from Script import script
from database.ia_filterdb import get_search_results, get_file_details
from utils.helpers import check_fsub, get_size, is_user_verified, get_verify_token, get_shortlink, HOW_TO_VERIFY, TUTORIAL
from utils.temp import temp

# --- ফিল্টার হ্যান্ডলার ---
@Client.on_message(filters.text & (filters.group | filters.private) & ~filters.command(["start", "stats", "broadcast", "addfsub", "delfsub", "fsublist"]))
@check_fsub
async def auto_filter_handler(client, message):
    # সার্চ কোয়েরি পরিষ্কার করা
    query = message.text
    search = re.sub(r'(_|\-|\.|\+|\(|\))', ' ', query).strip()
    
    if len(search) < 2:
        return

    # ডাটাবেস থেকে ফাইল খোঁজা হচ্ছে
    files, next_offset, total_results = await get_search_results(query=search, max_results=5)
    
    if not files:
        # বানান ভুলের জন্য সাজেশন (ঐচ্ছিক, পরে যোগ করা যেতে পারে)
        return

    # ফাইল পাঠানোর আগে ভেরিফিকেশন চেক
    if not await is_user_verified(message.from_user.id):
        token = await get_verify_token(message.from_user.id, files[0].file_id)
        verify_link = f"{URL}verify?token={token}" # ওয়েব সার্ভার রুট (পরে stream.py তে তৈরি হবে)
        short_verify_link = await get_shortlink(verify_link)

        buttons = [
            [InlineKeyboardButton("✅ Click Here to Verify ✅", url=short_verify_link)],
            [InlineKeyboardButton("💡 How to Verify 💡", url=HOW_TO_VERIFY)]
        ]
        await message.reply_text("ফাইলটি পেতে, অনুগ্রহ করে ভেরিফাই করুন।", reply_markup=InlineKeyboardMarkup(buttons))
        return

    # ফলাফল পাঠানোর জন্য বাটন তৈরি
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
            InlineKeyboardButton("Next ➡️", callback_data=f"next#{search}#{next_offset}")
        ])

    # ফলাফল পাঠানো হচ্ছে
    if IMDB:
        # IMDB ফিচার (পরে imdb.py প্লাগইন দিয়ে যুক্ত করা হবে)
        await message.reply_text(
            f"আপনার '{query}' এর জন্য {total_results} টি ফলাফল পাওয়া গেছে।",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    else:
        await message.reply_text(
            f"'{query}' এর জন্য ফলাফল:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )


@Client.on_callback_query(filters.regex(r'^file#'))
async def file_callback_handler(client, query):
    _, file_id = query.data.split("#")
    
    file_details = await get_file_details(file_id)
    if not file_details:
        return await query.answer("ফাইলটি খুঁজে পাওয়া যায়নি।")
    
    file_info = file_details[0]
    
    # লিঙ্ক শর্ট করা হচ্ছে
    main_link = f"https://t.me/{temp.BOT_USERNAME}?start=file_{file_id}"
    download_link = await get_shortlink(main_link)
    
    buttons = [
        [InlineKeyboardButton("📥 Download Now 📥", url=download_link)],
        [InlineKeyboardButton("💡 How to Download 💡", url=TUTORIAL)]
    ]
    
    # প্রাইভেট মেসেজে ফাইল পাঠানোর জন্য একটি বার্তা দেওয়া হচ্ছে
    await query.answer("ফাইলটি আপনার প্রাইভেট মেসেজে পাঠানো হচ্ছে...", show_alert=True)
    
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
