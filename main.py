from pyrogram import Client, filters
from pyrogram.types import Message
import os
import json
from dotenv import load_dotenv
import re

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

def escape_markdown(text: str) -> str:
    """
    Escape text for Telegram MarkdownV2.
    """
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)

app = Client("filestreambot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.private & (filters.document | filters.video | filters.audio | filters.photo))
async def save_file(client, message: Message):
    sent = await message.forward(STORAGE_CHAT_ID)
    file_key = str(sent.id)

    media = message.document or message.video or message.audio or message.photo

    file_name = getattr(media, "file_name", None)
    if not file_name and message.photo:
        file_name = "photo.jpg"  # fallback name for photos
    
    file_size = getattr(media, "file_size", 0)
    file_type = message.media  # e.g., "document", "video", etc.
    file_tg_id = media.file_id

    FILE_DB[file_key] = {
        "file_type": file_type,
        "file_id": file_tg_id,
        "file_name": file_name,
        "file_size": file_size
    }
    save_db()

    bot_username = (await client.get_me()).username
    start_link = f"https://t.me/{bot_username}?start={file_key}"

    reply_text = (
        f"📤 *File Uploaded Successfully!*\n\n"
        f"📁 *Name:* `{escape_markdown(file_name or 'Unknown')}`\n"
        f"📏 *Size:* `{round(file_size / 1024 / 1024, 2)} MB`\n"
        f"📦 *Type:* `{escape_markdown(file_type)}`\n"
        f"⚙️ *File ID:* `{escape_markdown(file_key)}`\n\n"
        f"🔗 *Shareable Link:*\n[Click Here]({start_link})\n\n"
        f"📥 *Send this link to anyone to let them download your file instantly!*"
    )

    await message.reply_text(
        reply_text,
        disable_web_page_preview=True,
        parse_mode="MarkdownV2"
    )

@app.on_message(filters.private & filters.command("start"))
async def send_file(client, message: Message):
    args = message.text.split(" ")
    if len(args) == 2:
        file_key = args[1]
        if file_key in FILE_DB:
            file_data = FILE_DB[file_key]
            caption = f"📥 *Here's your file!*\n📁 `{escape_markdown(file_data['file_name'] or 'Unknown')}`"
            
            # Send according to media type
            file_type = file_data["file_type"]
            file_id = file_data["file_id"]

            if file_type == "document":
                await message.reply_document(file_id, caption=caption, parse_mode="MarkdownV2")
            elif file_type == "video":
                await message.reply_video(file_id, caption=caption, parse_mode="MarkdownV2")
            elif file_type == "audio":
                await message.reply_audio(file_id, caption=caption, parse_mode="MarkdownV2")
            elif file_type == "photo":
                await message.reply_photo(file_id, caption=caption, parse_mode="MarkdownV2")
            else:
                # fallback to document
                await message.reply_document(file_id, caption=caption, parse_mode="MarkdownV2")
        else:
            await message.reply_text(
                "❌ *Sorry, this file was not found or has expired.*",
                parse_mode="MarkdownV2"
            )
    else:
        await message.reply_text(
            "👋 *Welcome to FileToLinks Bot!*\n\n"
            "🚀 _Send me any file, and I will generate a secure, shareable Telegram link for you instantly._\n\n"
            "📥 Just send a file to get started!",
            parse_mode="MarkdownV2"
        )

app.run()
