from pyrogram import Client, filters
from pyrogram.types import Message
import os
import json
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
STORAGE_CHAT_ID = int(os.getenv("STORAGE_CHAT_ID"))

# Load file database
if os.path.exists("files.json"):
    with open("files.json") as f:
        FILE_DB = json.load(f)
else:
    FILE_DB = {}

def save_db():
    with open("files.json", "w") as f:
        json.dump(FILE_DB, f)

app = Client("filestreambot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Get file type label
def get_file_label(file_name, media_type):
    if file_name.lower().endswith(".pdf"):
        return "📄 PDF Document"
    elif file_name.lower().endswith(".apk"):
        return "📱 APK File"
    elif file_name.lower().endswith(".zip"):
        return "🗜️ ZIP Archive"
    elif "video" in str(media_type).lower():
        return "🎞️ Video"
    elif "audio" in str(media_type).lower():
        return "🎵 Audio"
    elif "photo" in str(media_type).lower():
        return "🖼️ Photo"
    else:
        return "📁 Document"

# Handle file uploads
@app.on_message(filters.private & (filters.document | filters.video | filters.audio | filters.photo))
async def save_file(client, message: Message):
    sent = await message.forward(STORAGE_CHAT_ID)
    file_id = str(sent.id)

    media = message.document or message.video or message.audio or message.photo
    file_name = getattr(media, "file_name", "Unknown")
    file_size = getattr(media, "file_size", 0)
    file_type = message.media
    file_tg_id = media.file_id

    FILE_DB[file_id] = {
        "file_type": file_type,
        "file_id": file_tg_id,
        "file_name": file_name,
        "file_size": file_size
    }
    save_db()

    file_label = get_file_label(file_name, file_type)
    start_link = f"https://t.me/{(await client.get_me()).username}?start={file_id}"

    await message.reply_text(
        f"✨ **Premium File Uploaded!**\n\n"
        f"📁 **Name:** `{file_name}`\n"
        f"📦 **Type:** `{file_label}`\n"
        f"📏 **Size:** `{round(file_size / 1024 / 1024, 2)} MB`\n"
        f"🧬 **Hash ID:** `{file_id}`\n\n"
        f"🔗 **Direct Link:** [Click Here]({start_link})\n"
        f"⚡ Powered by *RetrivedMods FileBot*",
        disable_web_page_preview=True
    )

# Handle /start command
@app.on_message(filters.private & filters.command("start"))
async def send_file(client, message: Message):
    args = message.text.split(" ")
    if len(args) == 2:
        file_id = args[1]
        if file_id in FILE_DB:
            file_name = FILE_DB[file_id]['file_name']
            file_label = get_file_label(file_name, FILE_DB[file_id]['file_type'])
            await message.reply_document(
                FILE_DB[file_id]["file_id"],
                caption=(
                    f"📥 **Here's your premium file!**\n"
                    f"📁 {file_name}\n"
                    f"📦 Type: {file_label}\n"
                    f"💡 Powered by @RetrivedMods"
                )
            )
        else:
            await message.reply("❌ Sorry, this file link is invalid or expired.")
    else:
        await message.reply_photo(
            photo="https://retrivedmods.neocities.org/assets/channels4_profile.jpg",
            caption=(
                "**📂 Welcome to RetrivedMods FileBot!**\n\n"
                "🚀 Instantly turn any file into a shareable link.\n"
                "Supports: PDF, APK, ZIP, Photos, Videos, Music & more!\n"
                "🔒 Files are stored securely and can be retrieved anytime.\n\n"
                "✨ *Fast. Premium. Easy.*"
            ),
            parse_mode="Markdown"
        )

app.run()
