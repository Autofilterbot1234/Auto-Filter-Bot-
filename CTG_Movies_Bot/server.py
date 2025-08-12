import logging
from aiohttp import web

# লগিং সেটআপ
logger = logging.getLogger(__name__)

# রুট টেবিল তৈরি করা হচ্ছে
routes = web.RouteTableDef()

# --- রুট হ্যান্ডলারগুলো ---

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    """সার্ভারটি চলছে কিনা তা পরীক্ষা করার জন্য একটি বেসিক রুট"""
    return web.json_response({
        "server_status": "running",
        "bot_name": "CTG_Movies_Bot"
    })

# ফাইল স্ট্রিমিং এবং ডাউনলোডের জন্য রুট
@routes.get(r"/{media_id:\d+}/{file_name}", allow_head=True)
async def stream_handler(request: web.Request):
    """
    এই হ্যান্ডলারটি ফাইল ডাউনলোড এবং স্ট্রিম করার অনুরোধ গ্রহণ করে।
    মূল যুক্তিটি media_streamer ফাংশনে থাকবে যা আমরা পরে তৈরি করব।
    """
    try:
        media_id = int(request.match_info['media_id'])
        # media_streamer ফাংশনটি আমরা পরে একটি আলাদা প্লাগইনে তৈরি করব
        from plugins.stream import media_streamer 
        return await media_streamer(request, media_id)
    except Exception as e:
        logger.error(f"Error in stream handler: {e}", exc_info=True)
        return web.Response(status=500, text="Internal Server Error")

# --- ওয়েব সার্ভার অ্যাপ তৈরি করার ফাংশন ---
async def web_server():
    """aiohttp ওয়েব অ্যাপ্লিকেশন তৈরি করে এবং রুটগুলো যোগ করে"""
    web_app = web.Application(client_max_size=30000000)
    web_app.add_routes(routes)
    logger.info("Web server routes configured.")
    return web_app
