from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv
from fastapi import FastAPI
import threading
import uvicorn
import os
import json

# Load environment variables
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
STORAGE_CHAT_ID = int(os.getenv("STORAGE_CHAT_ID"))

# Load or initialize file database
if os.path.exists("files.json"):
    with open("files.json") as f:
        FILE_DB = json.load(f)
else:
    FILE_DB = {}

def save_db():
    with open("files.json", "w") as f:
        json.dump(FILE_DB, f)

# Initialize the bot
bot = Client(
    "filestreambot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# FastAPI instance
app = FastAPI()

@app.get("/")
def health():
    return {"status": "ok", "message": "Bot is running and healthy."}

# Pyrogram bot logic
@bot.on_message(filters.private & filters.command("help"))
async def help_command(client, message: Message):
    await message.reply_text("ℹ️ Help: Send me a file and I’ll give you a download link!")

@bot.on_message(filters.private & (filters.document | filters.video | filters.audio | filters.photo))
async def save_file(client, message: Message):
    try:
        sent = await message.forward(STORAGE_CHAT_ID)
        file_id = str(sent.id)

        media = message.document or message.video or message.audio or message.photo
        if isinstance(media, list):  # photos may be list
            media = media[-1]

        file_name = getattr(media, "file_name", "Unknown")
        file_size = getattr(media, "file_size", 0)
        file_type = message.media
        file_tg_id = media.file_id

        FILE_DB[file_id] = {
            "file_type": str(file_type),
            "file_id": file_tg_id,
            "file_name": file_name,
            "file_size": file_size
        }
        save_db()

        bot_username = (await client.get_me()).username
        start_link = f"https://t.me/{bot_username}?start={file_id}"

        await message.reply_text(
            f"**📤 Uploaded!**\n📁 `{file_name}`\n🔗 {start_link}"
        )
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

@bot.on_message(filters.private & filters.command("start"))
async def start(client, message: Message):
    args = message.text.split(" ")
    if len(args) == 2:
        file_id = args[1]
        if file_id in FILE_DB:
            data = FILE_DB[file_id]
            await message.reply_document(data["file_id"], caption=data["file_name"])
        else:
            await message.reply_text("❌ File not found or expired.")
    else:
        await message.reply_text("👋 Send me a file and I’ll give you a download link!")

# Run Pyrogram bot in a background thread
def run_bot():
    print("🤖 Starting Pyrogram bot...")
    bot.run()

# Entry point
if __name__ == "__main__":
    # Start the bot in a thread
    threading.Thread(target=run_bot, daemon=True).start()
    
    # Start FastAPI main thread (required for Koyeb)
    print("✅ Starting FastAPI server on port 8000...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
