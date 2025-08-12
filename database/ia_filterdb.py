import logging
from umongo import Instance, Document, fields
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError
from marshmallow.exceptions import ValidationError

from info import DATABASE_URIS, DATABASE_NAME, COLLECTION_NAME
from utils import unpack_new_file_id

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# --- ডায়নামিকভাবে সব ডাটাবেস ক্লায়েন্ট এবং মডেল তৈরি ---
mongo_clients = [AsyncIOMotorClient(uri) for uri in DATABASE_URIS]
dbs = [client[DATABASE_NAME] for client in mongo_clients]
instances = [Instance.from_db(db) for db in dbs]

MediaModels = []
for i, instance in enumerate(instances):
    @instance.register
    class Media(Document):
        file_id = fields.StrField(attribute='_id')
        file_name = fields.StrField(required=True)
        file_size = fields.IntField(required=True)
        file_type = fields.StrField(allow_none=True)
        caption = fields.StrField(allow_none=True)

        class Meta:
            indexes = ('$file_name',)
            collection_name = f"{COLLECTION_NAME}_{i+1}"
    MediaModels.append(Media)

logger.info(f"Initialized {len(MediaModels)} database(s).")

# --- পরবর্তী উপলব্ধ ডাটাবেস খুঁজে বের করার ফাংশন ---
async def get_next_db_model():
    for i, client in enumerate(mongo_clients):
        try:
            stats = await client[DATABASE_NAME].command('dbStats')
            # 512MB ফ্রি টিয়ারের 95% (486MB) পূর্ণ হলে পরবর্তী ডাটাবেসে যাবে
            if (stats.get('dataSize', 0) + stats.get('indexSize', 0)) < 486 * 1024 * 1024:
                logger.info(f"Using Database {i+1} for saving new files.")
                return MediaModels[i]
        except Exception as e:
            logger.error(f"Could not connect or get stats for DB {i+1}: {e}")
            continue
    logger.warning("All databases are full or unavailable!")
    return None

# --- ফাইল সেভ করার ফাংশন ---
async def save_file(media):
    SaveMediaModel = await get_next_db_model()
    if not SaveMediaModel:
        return False, "All databases are full."

    file_id = media.file_id
    file_name = media.file_name.replace('_', ' ')
    
    for model in MediaModels:
        if await model.find_one({'_id': file_id}):
            logger.warning(f"'{file_name}' is already saved in another database.")
            return False, 0
    
    try:
        file_doc = SaveMediaModel(
            file_id=file_id,
            file_name=file_name,
            file_size=media.file_size,
            file_type=media.file_type,
            caption=getattr(media, 'caption', '')
        )
        await file_doc.commit()
        return True, 1
    except DuplicateKeyError:
        logger.warning(f"'{file_name}' is already saved in the current database.")
        return False, 0
    except ValidationError as e:
        logger.error(f'Validation Error while saving file: {e}')
        return False, 2

# --- সার্চ এবং অন্যান্য ফাংশন ---
async def get_search_results(query, file_type=None, max_results=10, offset=0):
    all_files = []
    
    # সব ডাটাবেসে একসাথে সার্চ করা হচ্ছে
    for model in MediaModels:
        filter_ = {'file_name': {'$regex': query, '$options': 'i'}}
        if file_type:
            filter_['file_type'] = file_type
        
        files = await model.find(filter_).to_list(length=None)
        all_files.extend(files)

    # সব ফলাফল একত্রিত করে সর্ট করা
    all_files.sort(key=lambda x: x.id, reverse=True)
    
    total_results = len(all_files)
    paginated_files = all_files[offset : offset + max_results]
    
    next_offset = offset + len(paginated_files)
    if next_offset >= total_results:
        next_offset = ''
        
    return paginated_files, next_offset, total_results

async def get_file_details(file_id):
    for model in MediaModels:
        file_details = await model.find_one({'_id': file_id})
        if file_details:
            return [file_details]
    return []
