LnvNjE' re
import os
from os import environ

# আপনার স্ক্রিপ্ট ফাইল যদি "script.py" নামে হয়, তাহলে এই লাইনটি এভাবে ঠিক করুন:
from script import script  

# --- Utility Functions ---
id_pattern = re.compile(r'^.\d+$')
def is_enabled(value, default):
    if str(value).lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif str(value).lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default

# --- Bot Information ---
API_ID = int(environ.get('API_ID', '20632324'))
API_HASH = environ.get('API_HASH', '7472998b241dd149fc2b2167ce045c0e')
BOT_TOKEN = environ.get('BOT_TOKEN', '8323096986:AAG5leTxjaOty2aHkV-MvAR1FfR79LnvNjE')
SESSION = environ.get('SESSION', 'CTG_Movies_Bot')

# --- Database Configuration (5 Separate Databases) ---
DATABASE_1 = environ.get('DATABASE_1', "mongodb+srv://yimiva2523:yimiva2523@cluster0.zvaaxhh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DATABASE_2 = environ.get('DATABASE_2', "")
DATABASE_3 = environ.get('DATABASE_3', "")
DATABASE_4 = environ.get('DATABASE_4', "")
DATABASE_5 = environ.get('DATABASE_5', "")
DATABASE_URIS = [uri for uri in [DATABASE_1, DATABASE_2, DATABASE_3, DATABASE_4, DATABASE_5] if uri]
DATABASE_NAME = environ.get('DATABASE_NAME', "Cluster0")
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'MoviesCollection')

# --- Admins and Channel IDs ---
ADMINS = [int(admin) for admin in environ.get('ADMINS', '5370676246 8090888302').split()]
LOG_CHANNEL = int(environ.get('LOG_CHANNEL', '-1002724644600'))
CHANNELS = [int(ch) for ch in environ.get('CHANNELS', '-1002728760268').split()]

# --- Custom Links ---
GRP_LNK = environ.get('GRP_LNK', 'https://t.me/Movie_Request_Group_23')
OWNER_LNK = environ.get('OWNER_LNK', 'https://t.me/ctgmovies23')

# --- Verification System Configuration ---
VERIFY = is_enabled(environ.get('VERIFY', False), False)
VERIFY_EXPIRE = int(environ.get('VERIFY_EXPIRE', 24))
VERIFIED_LOG = int(environ.get('VERIFIED_LOG', LOG_CHANNEL))
HOW_TO_VERIFY = environ.get('HOW_TO_VERIFY', 'https://t.me/HowToVerifyTutorial')

# --- Link Shortener Configuration ---
IS_SHORTLINK = is_enabled(environ.get('IS_SHORTLINK', False), False)
SHORTLINK_URL = environ.get('SHORTLINK_URL', 'adrinolinks.in')
SHORTLINK_API = environ.get('SHORTLINK_API', 'your_api_key')
TUTORIAL = environ.get('TUTORIAL', 'https://t.me/HowToDownload')

# --- Bot Behavior ---
PROTECT_CONTENT = is_enabled(environ.get('PROTECT_CONTENT', True), True)
IMDB = is_enabled(environ.get('IMDB', True), True)
AUTO_DELETE = is_enabled(environ.get('AUTO_DELETE', True), True)
DELETE_TIME = int(environ.get("DELETE_TIME", 300))

# --- Web Server ---
PORT = int(environ.get("PORT", 8080))
ON_HEROKU = is_enabled(environ.get("ON_HEROKU", False), False)
FQDN = environ.get("FQDN", "localhost")
if ON_HEROKU:
    APP_NAME = environ.get('APP_NAME')
    if APP_NAME:
        FQDN = f"{APP_NAME}.herokuapp.com"
URL = f"https://{FQDN}/"

# --- Media ---
PICS = (environ.get('PICS', 'https://telegra.ph/file/0de93c78a050f8c826622.jpg')).split()
FSUB_PICS = (environ.get('FSUB_PICS', 'https://telegra.ph/file/7478ff3eac37f4329c3d8.jpg')).split()

# --- Custom captions and templates ---
CUSTOM_FILE_CAPTION = environ.get("CUSTOM_FILE_CAPTION", "<b>{file_name}</b>\n\n<b>Join & Support Us ❤️</b>")
IMDB_TEMPLATE = environ.get("IMDB_TEMPLATE", script.IMDB_TEMPLATE_TXT)
