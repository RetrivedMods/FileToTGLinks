from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
import os
import json
from dotenv import load_dotenv
from flask import Flask
import threading

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

@bot.on_message(filters.private & filters.command("help"))
async def help_command(client, message: Message):
    await message.reply_text(
        "👋 **Welcome to FileToLinks Bot**\n"
        "🚀 _Your personal file uploader and sharer made simple._\n\n"
        "📦 **What Can I Do?**\n"
        "• Convert any file into a downloadable Telegram link.\n"
        "• Supports documents (APK, ZIP, etc), videos, audios, images, and more.\n\n"
        "📖 **How to Use:**\n"
        "1️⃣ Send me a file (any type).\n"
        "2️⃣ Wait a moment while I process it.\n"
        "3️⃣ Get your secure shareable download link.\n\n"
        "🛠 **Need Help?** Contact [@WClientOwner](https://t.me/WClientOwner)\n\n"
        "`/start` - Show welcome or retrieve file\n"
        "`/help` - Show this message again",
        disable_web_page_preview=True,
        parse_mode="Markdown"
    )

@bot.on_message(filters.private & (filters.document | filters.video | filters.audio | filters.photo))
async def save_file(client, message: Message):
    try:
        sent = await message.forward(STORAGE_CHAT_ID)
        file_id = str(sent.id)

        media = message.document or message.video or message.audio or message.photo
        if isinstance(media, list):
            media = media[-1]  # For photo array (highest resolution)

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
            f"📤 **File Uploaded!**\n\n"
            f"📁 Name: `{file_name}`\n"
            f"📏 Size: `{round(file_size / 1024 / 1024, 2)} MB`\n"
            f"📦 Type: `{file_type}`\n"
            f"⚙️ Hash: `{file_id}`\n\n"
            f"🔗 **Share Link:**\n`{start_link}`\n\n"
            f"📋 *Tap the link above to copy it.*",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔗 Open Link", url=start_link)
            ]]),
            parse_mode="Markdown"
        )

    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@bot.on_message(filters.private & filters.command("start"))
async def send_file(client, message: Message):
    try:
        args = message.text.split(" ")
        if len(args) == 2:
            file_id = args[1]
            if file_id in FILE_DB:
                file_data = FILE_DB[file_id]
                file_type = file_data["file_type"].lower()

                if "document" in file_type:
                    await message.reply_document(
                        file_data["file_id"],
                        caption=f"📥 **Here's your file!**\n📁 {file_data['file_name']}"
                    )
                elif "video" in file_type:
                    await message.reply_video(
                        file_data["file_id"],
                        caption=f"📥 **Here's your file!**\n📁 {file_data['file_name']}"
                    )
                elif "audio" in file_type:
                    await message.reply_audio(
                        file_data["file_id"],
                        caption=f"📥 **Here's your file!**\n📁 {file_data['file_name']}"
                    )
                elif "photo" in file_type:
                    await message.reply_photo(
                        file_data["file_id"],
                        caption=f"📥 **Here's your file!**\n📁 {file_data['file_name']}"
                    )
                else:
                    await message.reply_document(
                        file_data["file_id"],
                        caption=f"📥 **Here's your file!**\n📁 {file_data['file_name']}"
                    )
            else:
                await message.reply_text("❌ File not found or expired.")
        else:
            await message.reply_photo(
                photo="https://retrivedmods.neocities.org/assets/channels4_profile.jpg",
                caption=(
                    "**📂 File To Links Bot**\n\n"
                    "🚀 *Convert any file into a downloadable link instantly!*\n"
                    "🔗 Share links easily with friends or embed anywhere.\n"
                    "🛡️ 100% secure, fast, and free.\n\n"
                    "📥 *Send me a file, and I'll generate a Telegram link for you!*"
                ),
                parse_mode="Markdown"
            )

    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

# Flask app for uptime pings
app = Flask("")

@app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# Main runner
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    print("Bot is starting...")
    bot.run()
