import logging
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.users_chats_db import db
from info import ADMINS

logger = logging.getLogger(__name__)

# চ্যানেল তথ্য পাওয়ার জন্য হেল্পার ফাংশন
async def get_channel_info(client, channel_id):
    try:
        chat = await client.get_chat(channel_id)
        return chat.title, chat.username
    except Exception as e:
        logger.error(f"Error getting info for channel {channel_id}: {e}")
        return f"Unknown Channel", None

@Client.on_message(filters.command("addfsub") & filters.user(ADMINS))
async def add_fsub_command(client, message):
    if len(message.command) != 3:
        await message.reply_text(
            "<b>ব্যবহারের নিয়ম:</b>\n`/addfsub <channel_id> <public/private>`\n\n"
            "<b>উদাহরণ:</b>\n`/addfsub -10012345678 public`"
        )
        return

    try:
        channel_id = int(message.command[1])
        channel_type = message.command[2].lower()

        if channel_type not in ["public", "private"]:
            await message.reply_text("চ্যানেলের ধরণ অবশ্যই `public` অথবা `private` হতে হবে।")
            return
            
        if await db.is_fsub_channel_exist(channel_id):
            await message.reply_text("এই চ্যানেলটি ইতোমধ্যে তালিকায় যুক্ত আছে।")
            return

        try:
            member = await client.get_chat_member(channel_id, "me")
            if member.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
                await message.reply_text("এই চ্যানেলে আমাকে অ্যাডমিন হিসেবে যুক্ত করুন এবং আবার চেষ্টা করুন।")
                return
        except Exception:
            await message.reply_text("চ্যানেল আইডিটি ভুল অথবা আমি ওই চ্যানেলের সদস্য নই।")
            return

        await db.add_fsub_channel(channel_id, channel_type)
        title, _ = await get_channel_info(client, channel_id)
        await message.reply_text(f"✅ চ্যানেল '{title}' (`{channel_id}`) সফলভাবে `{channel_type}` হিসেবে যুক্ত করা হয়েছে।")

    except ValueError:
        await message.reply_text("চ্যানেল আইডি অবশ্যই একটি সংখ্যা হতে হবে।")
    except Exception as e:
        await message.reply_text(f"একটি সমস্যা হয়েছে: {e}")


@Client.on_message(filters.command("delfsub") & filters.user(ADMINS))
async def del_fsub_command(client, message):
    if len(message.command) != 2:
        await message.reply_text("<b>ব্যবহারের নিয়ম:</b> `/delfsub <channel_id>`")
        return

    try:
        channel_id = int(message.command[1])
        
        if not await db.is_fsub_channel_exist(channel_id):
            await message.reply_text("এই চ্যানেলটি তালিকায় খুঁজে পাওয়া যায়নি।")
            return

        await db.remove_fsub_channel(channel_id)
        await message.reply_text(f"🗑️ চ্যানেল `{channel_id}` তালিকা থেকে সফলভাবে মুছে ফেলা হয়েছে।")

    except ValueError:
        await message.reply_text("চ্যানেল আইডি অবশ্যই একটি সংখ্যা হতে হবে।")
    except Exception as e:
        await message.reply_text(f"একটি সমস্যা হয়েছে: {e}")


@Client.on_message(filters.command("fsublist") & filters.user(ADMINS))
async def fsub_list_command(client, message):
    public, private = await db.get_fsub_channels()
    
    if not public and not private:
        await message.reply_text("ফোর্স সাবস্ক্রাইবের জন্য কোনো চ্যানেল যুক্ত করা নেই।")
        return

    text = "📜 **ফোর্স সাবস্ক্রাইব চ্যানেলের তালিকা:**\n\n"

    text += "🌐 **পাবলিক চ্যানেল (জয়েন থাকতে হবে):**\n"
    if public:
        for cid in public:
            title, _ = await get_channel_info(client, cid)
            text += f" - `{cid}` ({title})\n"
    else:
        text += " - কোনো পাবলিক চ্যানেল নেই।\n"

    text += "\n🔒 **প্রাইভেট চ্যানেল (রিকোয়েস্ট পাঠাতে হবে):**\n"
    if private:
        for cid in private:
            title, _ = await get_channel_info(client, cid)
            text += f" - `{cid}` ({title})\n"
    else:
        text += " - কোনো প্রাইভেট চ্যানেল নেই।"

    await message.reply_text(text)
