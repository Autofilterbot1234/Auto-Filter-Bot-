class script(object):
    
    # --- স্টার্ট কমান্ডের বার্তা ---
    START_TXT = """<b>👋 হ্যালো {mention},</b>

আমি একটি অটো ফিল্টার বট। গ্রুপে যেকোনো মুভির নাম লিখে সার্চ করুন, আমি আপনাকে ফাইল খুঁজে দেব।

<b>Developed by <a href='https://t.me/ctgmovies23'>CTG Movies</a></b>"""

    # --- গ্রুপে স্টার্ট কমান্ডের বার্তা ---
    G_START_TXT = """<b>✅ আমি এই গ্রুপে সঠিকভাবে কাজ করছি।</b>"""

    # --- About কমান্ডের বার্তা ---
    ABOUT_TXT = """
<b>⚜️ আমার নাম: {bot_name}</b>
<b>⚜️ ডেভেলপার: <a href='{owner_link}'>CTG Movies</a></b>
<b>⚜️ লাইব্রেরি: <a href='https://docs.pyrogram.org/'>Pyrogram</a></b>
<b>⚜️ ভাষা: <a href='https://www.python.org/'>Python 3</a></b>
<b>⚜️ ডাটাবেস: <a href='https://www.mongodb.com/'>Mongo DB</a></b>
"""

    # --- ফাইল না পাওয়া গেলে বার্তা ---
    FILE_NOT_FND_TXT = """<b>🥲 দুঃখিত, আমি আপনার অনুরোধ করা "{query}" খুঁজে পাইনি।</b>

অনুগ্রহ করে নামের বানান পরীক্ষা করে আবার চেষ্টা করুন।"""

    # --- বানান ভুলের জন্য সাজেশন বার্তা ---
    SPELL_CHECK_TXT = """<b>আপনি কি "{correct_spell}" খুঁজছেন?

অনুগ্রহ করে নিচের বাটন থেকে সঠিক নামটি বেছে নিন।</b>"""

    # --- IMDB টেমপ্লেট ---
    IMDB_TEMPLATE_TXT = """
<b>🏷 Title:</b> <a href={url}>{title}</a>
<b>🎭 Genres:</b> {genres}
<b>📆 Year:</b> <a href={url}/releaseinfo>{year}</a>
<b>🌟 Rating:</b> <a href={url}/ratings>{rating}/10</a>
"""

    # --- স্ট্যাটাস (Stats) কমান্ডের বার্তা ---
    STATUS_TXT = """<b>BOT STATUS</b>

<b>Total Files in DB:</b> {total_files}
<b>Total Users:</b> {total_users}
<b>Total Chats:</b> {total_chats}

<b><u>Database Usage:</u></b>
{db_status}
"""
