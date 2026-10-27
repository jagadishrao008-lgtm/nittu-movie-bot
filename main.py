import logging
import asyncio
from aiohttp import web
from pyrogram import Client, filters
from motor.motor_asyncio import AsyncIOMotorClient

logging.basicConfig(level=logging.INFO)

API_ID = 35992347
API_HASH = "a3c7960f6fb6a8b4cd3cdd9f4b93737f"
BOT_TOKEN = "8791951760:AAHCTPRz1lfzZILE0Uhye7rHQphxKnZ1urQ"
CHANNEL_ID = -1001813593588
MONGO_URL = "mongodb+srv://jagadishrao008_db_user:OwRNyuQsYWxyH3VB@cluster0.mongodb.net/?retryWrites=true&w=majority"

app = Client("NittuMovieFilter", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
db_client = AsyncIOMotorClient(MONGO_URL)
db = db_client["NittuMovieDB"]
collection = db["files"]

@app.on_message(filters.command("start"))
async def start_handler(client, message):
    await message.reply_text(
        "👋 హాయ్ అన్నా!\n"
        "నేను మీ **Nittu Movie Filter Bot** ని.\n"
        "మీ గ్రూప్‌లో సినిమా పేరు టైప్ చేస్తే చాలు, నేను ఆ సినిమాని వెతికి ఇస్తాను! 🎬"
    )

@app.on_message(filters.chat(CHANNEL_ID) & (filters.document | filters.video | filters.audio))
async def index_files(client, message):
    media = message.document or message.video or message.audio
    if media:
        file_name = media.file_name or "Unknown"
        file_id = media.file_id
        await collection.update_one(
            {"file_id": file_id},
            {"$set": {"file_name": file_name, "file_id": file_id}},
            upsert=True
        )

@app.on_message(filters.group & ~filters.command("start"))
async def search_files(client, message):
    query = message.text
    if not query:
        return
    
    results = await collection.find({"file_name": {"$regex": query, "$options": "i"}}).to_list(length=10)
    
    if not results:
        await message.reply_text("❌ క్షమించండి, ఆ సినిమా మన డేటాబేస్‌లో దొరకలేదు.")
        return
    
    for file in results:
        f_name = file["file_name"]
        f_id = file["file_id"]
        await client.send_cached_media(message.chat.id, file_id=f_id, caption=f"🎬 **{f_name}**\n📥 Powered by Nittu Movies")

async def web_server():
    routes = web.RouteTableDef()
    @routes.get("/")
    async def hello_handler(request):
        return web.Response(text="Nittu Movie Bot is Alive!")
    
    web_app = web.Application()
    web_app.add_routes(routes)
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()

async def main():
    await app.start()
    print("✨ టెలిగ్రామ్ బాట్ విజయవంతంగా స్టార్ట్ అయింది!")
    await web_server()
    print("🚀 రెండర్ వెబ్ సర్వర్ లైవ్‌లో ఉంది!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
  
