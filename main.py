import logging
import asyncio
from aiohttp import web
from pyrogram import Client
from motor.motor_asyncio import AsyncIOMotorClient

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "8791951760:AAHCTPRz1lfzZILE0Uhye7rHQphxKnZ1urQ"
CHANNEL_ID = -1001813593588
MONGO_URL = "mongodb+srv://jagadishrao008_db_user:OwRNyuQsYWxyH3VB@cluster0.mongodb.net/?retryWrites=true&w=majority"

# ఇక్కడ api_id, api_hash పూర్తిగా తొలగించబడ్డాయి
app = Client(
    "NittuMovieFilter",
    bot_token=BOT_TOKEN
)

db_client = AsyncIOMotorClient(MONGO_URL)
db = db_client["NittuMovieDB"]
collection = db["files"]

@app.on_message()
async def all_messages(client, message):
    if message.chat and message.chat.id == CHANNEL_ID:
        media = message.document or message.video or message.audio
        if media:
            await collection.update_one(
                {"file_id": media.file_id},
                {"$set": {"file_name": media.file_name or "Unknown", "file_id": media.file_id}},
                upsert=True
            )
    elif message.text and not message.text.startswith("/"):
        query = message.text
        results = await collection.find({"file_name": {"$regex": query, "$options": "i"}}).to_list(length=10)
        for file in results:
            await client.send_cached_media(message.chat.id, file_id=file["file_id"], caption=f"🎬 **{file['file_name']}**\n📥 Powered by Nittu Movies")

async def web_server():
    routes = web.RouteTableDef()
    @routes.get("/")
    async def hello(request):
        return web.Response(text="Bot is running!")
    web_app = web.Application()
    web_app.add_routes(routes)
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()

async def main():
    await app.start()
    print("Bot started successfully!")
    await web_server()
    await asyncio.Event().wait()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    
    
    
    
  
