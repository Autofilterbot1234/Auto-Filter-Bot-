import logging
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from info import ADMINS
from database.ia_filterdb import MediaModels

logger = logging.getLogger(__name__)

@Client.on_message(filters.command("delete") & filters.user(ADMINS))
async def delete_files_command(client, message):
    if len(message.command) == 1:
        return await message.reply_text(
            "<b>ব্যবহারের নিয়ম:</b> `/delete <keyword>`\n\n"
            "এই কমান্ডটি আপনার দেওয়া কিওয়ার্ড সম্পর্কিত সব ফাইল ডাটাবেস থেকে মুছে ফেলবে।"
        )
    
    keyword = message.text.split(" ", 1)[1]
    
    buttons = [
        [
            InlineKeyboardButton("✅ Yes, Delete ✅", callback_data=f"confirm_delete_keyword#{keyword}"),
            InlineKeyboardButton("❌ No, Cancel ❌", callback_data="cancel_delete")
        ]
    ]
    
    await message.reply_text(
        f"আপনি কি নিশ্চিত যে আপনি '<b>{keyword}</b>' সম্পর্কিত সব ফাইল ডাটাবেস থেকে মুছে ফেলতে চান?\n\n"
        "<b>⚠️ এই কাজটি আর ফেরানো যাবে না!</b>",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_message(filters.command("deleteall") & filters.user(ADMINS))
async def delete_all_files_command(client, message):
    buttons = [
        [
            InlineKeyboardButton("🔴 YES, DELETE ALL 🔴", callback_data="confirm_delete_all"),
            InlineKeyboardButton("🟢 CANCEL 🟢", callback_data="cancel_delete")
        ]
    ]
    await message.reply_text(
        "আপনি কি নিশ্চিত যে আপনি **সমস্ত ডাটাবেস থেকে সব ফাইল** মুছে ফেলতে চান?\n\n"
        "<b>⚠️⚠️⚠️ এই কাজটি অত্যন্ত ঝুঁকিপূর্ণ এবং কোনোভাবেই ফেরানো যাবে না!</b>",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r'^confirm_delete_keyword#'))
async def confirm_delete_keyword_callback(client, query):
    _, keyword = query.data.split("#")
    await query.message.edit_text(f"'{keyword}' সম্পর্কিত ফাইলগুলো খোঁজা হচ্ছে এবং মোছা শুরু হচ্ছে...")
    
    deleted_count = 0
    total_files_checked = 0
    
    for model in MediaModels:
        try:
            # Regex ব্যবহার করে কিওয়ার্ড দিয়ে ফাইল খোঁজা হচ্ছে
            filter_ = {'file_name': {'$regex': keyword, '$options': 'i'}}
            result = await model.collection.delete_many(filter_)
            deleted_count += result.deleted_count
        except Exception as e:
            logger.error(f"Error deleting files from a DB collection: {e}")

    await query.message.edit_text(f"✅ সম্পন্ন!\n\n`{deleted_count}` টি ফাইল সফলভাবে মুছে ফেলা হয়েছে।")

@Client.on_callback_query(filters.regex(r'^confirm_delete_all$'))
async def confirm_delete_all_callback(client, query):
    await query.message.edit_text("সমস্ত ফাইল মোছা শুরু হচ্ছে... এটি কিছু সময় নিতে পারে।")
    
    deleted_count = 0
    try:
        for model in MediaModels:
            count = await model.count_documents({})
            await model.collection.drop() # সম্পূর্ণ কালেকশন ড্রপ করা হচ্ছে
            deleted_count += count
    except Exception as e:
        logger.error(f"Error dropping collections: {e}")
        return await query.message.edit_text(f"একটি সমস্যা হয়েছে: {e}")
        
    await query.message.edit_text(f"✅ সম্পন্ন!\n\nসমস্ত ডাটাবেস থেকে মোট `{deleted_count}` টি ফাইল সফলভাবে মুছে ফেলা হয়েছে।")
    
@Client.on_callback_query(filters.regex(r'^cancel_delete$'))
async def cancel_delete_callback(client, query):
    await query.message.edit_text("❌ ফাইল মোছার প্রক্রিয়া বাতিল করা হয়েছে।")
