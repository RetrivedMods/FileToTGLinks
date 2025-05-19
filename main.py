from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
import os
import json
from dotenv import load_dotenv
from flask import Flask
import threading
import re

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

# Escape text for Telegram MarkdownV2 formatting
def escape_markdown(text: str) -> str:
    """
    Escape special characters for Telegram MarkdownV2:
    _ * [ ] ( ) ~ ` > # + - = | { } . !
    """
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

# Initialize the bot client
bot = Client(
    "filestreambot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@bot.on_message(filters.private & filters.command("help"))
async def help_command(client, message: Message):
    text = (
        "👋 *Welcome to FileToLinks Bot*\n"
        "🚀 _Your personal file uploader and sharer made simple._\n\n"

        "📦 *What Can I Do?*\n"
        "• Convert any file you send into a shareable download link.\n"
        "• Supports documents, videos, audios, images, APKs, ZIPs, and more.\n"
        "• Receive an instant download URL with file name, size, and details.\n\n"

        "📖 *How to Use:*\n"
        "1️⃣ Send me a file (any type).\n"
        "2️⃣ Wait a moment while I process it.\n"
        "3️⃣ Get your download link with file info and a copyable link.\n\n"

        "📌 *Limitations:*\n"
        "• Maximum file size depends on Telegram limits (~2GB).\n"
        "• Link availability depends on file availability on Telegram servers.\n"
        "• This bot does not store files externally – it uses Telegram’s CDN.\n\n"

        "🛠 *Need Help?*\n"
        "If you face any issues or have suggestions,\n"
        "contact the developer: [@WClientOwner](https://t.me/WClientOwner)\n\n"

        "ℹ️ *Commands:*\n"
        "`/start` - Show welcome/help message or retrieve a file.\n"
        "`/help` - Display this help section again."
    )
    await message.reply_text(
        escape_markdown(text),
        disable_web_page_preview=True,
        parse_mode="MarkdownV2"
    )


@bot.on_message(filters.private & (filters.document | filters.video | filters.audio | filters.photo | filters.animation))
async def save_file(client, message: Message):
    try:
        sent = await message.forward(STORAGE_CHAT_ID)
        file_id = str(sent.id)

        media = message.document or message.video or message.audio or message.photo or message.animation

        if isinstance(media, list):
            media = media[-1]  # pick highest quality if photo is list

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

        reply_text = (
            f"📤 *File Uploaded!*\n\n"
            f"📁 Name: `{escape_markdown(file_name)}`\n"
            f"📏 Size: `{round(file_size / 1024 / 1024, 2)} MB`\n"
            f"📦 Type: `{escape_markdown(str(file_type))}`\n"
            f"⚙️ Hash: `{escape_markdown(file_id)}`\n\n"
            f"🔗 *Share Link:*\n`{start_link}`\n\n"
            f"📋 *Tap the link above to copy it.*"
        )

        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🔗 Open Link", url=start_link),
                    InlineKeyboardButton("📢 Join Channel", url="https://t.me/RetrivedMods")
                ],
                [
                    InlineKeyboardButton("🛠 Support", url="https://t.me/WClientOwner")
                ]
            ]
        )

        await message.reply_text(
            reply_text,
            reply_markup=buttons,
            parse_mode="MarkdownV2"
        )

    except Exception as e:
        await message.reply_text(
            f"❌ Error: {escape_markdown(str(e))}",
            parse_mode="MarkdownV2"
        )


@bot.on_message(filters.private & filters.command("start"))
async def send_file(client, message: Message):
    try:
        args = message.text.split(" ")
        if len(args) == 2:
            file_id = args[1]
            if file_id in FILE_DB:
                file_data = FILE_DB[file_id]
                file_type = file_data["file_type"].lower()

                caption = f"📥 *Here's your file!*\n📁 {escape_markdown(file_data['file_name'])}"

                if "document" in file_type or "application" in file_type:
                    await message.reply_document(
                        file_data["file_id"],
                        caption=caption,
                        parse_mode="MarkdownV2"
                    )
                elif "video" in file_type:
                    await message.reply_video(
                        file_data["file_id"],
                        caption=caption,
                        parse_mode="MarkdownV2"
                    )
                elif "audio" in file_type:
                    await message.reply_audio(
                        file_data["file_id"],
                        caption=caption,
                        parse_mode="MarkdownV2"
                    )
                elif "photo" in file_type:
                    await message.reply_photo(
                        file_data["file_id"],
                        caption=caption,
                        parse_mode="MarkdownV2"
                    )
                elif "animation" in file_type:
                    await message.reply_animation(
                        file_data["file_id"],
                        caption=caption,
                        parse_mode="MarkdownV2"
                    )
                else:
                    # fallback
                    await message.reply_document(
                        file_data["file_id"],
                        caption=caption,
                        parse_mode="MarkdownV2"
                    )
            else:
                await message.reply_text(
                    "❌ *File not found or expired.*",
                    parse_mode="MarkdownV2"
                )
        else:
            await message.reply_photo(
                photo="https://retrivedmods.neocities.org/assets/channels4_profile.jpg",
                caption=(
                    "*📂 File To Links Bot*\n\n"
                    "🚀 _Convert any file into a downloadable link instantly!_\n"
                    "🔗 Share links easily with friends or embed anywhere.\n"
                    "🛡️ 100% secure, fast, and free.\n\n"
                    "📥 _Send me a file, and I'll generate a telegram link for you!_"
                ),
                parse_mode="MarkdownV2"
            )

    except Exception as e:
        await message.reply_text(
            f"❌ Error: {escape_markdown(str(e))}",
            parse_mode="MarkdownV2"
        )

# Flask app to keep the bot alive on hosting services
app = Flask("")

@app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    # Run Flask in a background thread
    threading.Thread(target=run_flask).start()
    print("Bot is starting...")
    bot.run()
