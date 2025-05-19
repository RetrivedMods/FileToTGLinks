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
        "**👋 Welcome to FileToLinks Bot**\n"
        "🚀 *Your personal file uploader and sharer made simple.*\n\n"

        "**📦 What Can I Do?**\n"
        "• Convert any file you send into a shareable download link.\n"
        "• Supports documents, videos, audios, images, APKs, ZIPs, and more.\n"
        "• Receive an instant download URL with file name, size, and details.\n\n"

        "**📖 How to Use:**\n"
        "1️⃣ Send me a file (any type).\n"
        "2️⃣ Wait a moment while I process it.\n"
        "3️⃣ Get your download link with file info and a copyable link.\n\n"

        "**📌 Limitations:**\n"
        "• Max file size depends on Telegram limits (~2GB).\n"
        "• Link availability depends on Telegram server availability.\n"
        "• This bot uses Telegram's CDN; files aren't stored externally.\n\n"

        "**🛠 Need Help?**\n"
        "For issues or suggestions, contact the dev: [@WClientOwner](https://t.me/WClientOwner)\n\n"

        "**ℹ️ Commands:**\n"
        "`/start` - Show welcome/help or retrieve file\n"
        "`/help` - Display this help section again."
    )


@bot.on_message(filters.private & (filters.document | filters.video | filters.audio | filters.photo))
async def save_file(client, message: Message):
    try:
        sent = await message.forward(STORAGE_CHAT_ID)
        file_id = str(sent.id)

        # Get the actual media object
        media = message.document or message.video or message.audio or message.photo

        # Handle photo lists if any (usually photo is a single object)
        if isinstance(media, list):
            media = media[-1]  # highest quality photo

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
            f"**📤 File Uploaded!**\n\n"
            f"**📁 Name:** `{file_name}`\n"
            f"**📏 Size:** `{round(file_size / 1024 / 1024, 2)} MB`\n"
            f"**📦 Type:** `{file_type}`\n"
            f"**⚙️ Hash:** `{file_id}`\n\n"
            f"**🔗 Share Link:**\n[Click Here]({start_link})",
            disable_web_page_preview=True
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

                caption_text = (
                    f"📥 **Your file is ready!**\n\n"
                    f"📁 **Name:** `{file_data['file_name']}`\n"
                    f"🔗 **Type:** `{file_data['file_type'].split('.')[-1].upper()}`\n\n"
                    f"✨ *Powered by* [RetrivedMods](https://t.me/RetrivedMods)"
                )

                if "document" in file_type:
                    await message.reply_document(
                        file_data["file_id"],
                        caption=caption_text
                    )
                elif "video" in file_type:
                    await message.reply_video(
                        file_data["file_id"],
                        caption=caption_text
                    )
                elif "audio" in file_type:
                    await message.reply_audio(
                        file_data["file_id"],
                        caption=caption_text
                    )
                elif "photo" in file_type:
                    await message.reply_photo(
                        file_data["file_id"],
                        caption=caption_text
                    )
                else:
                    # fallback to document
                    await message.reply_document(
                        file_data["file_id"],
                        caption=caption_text
                    )
            else:
                await message.reply_text("❌ File not found or expired.")
        else:
            await message.reply_photo(
                photo="https://retrivedmods.neocities.org/assets/channels4_profile.jpg",
                caption=(
                    "**📂 Welcome to RetrivedMods File To Link Bot!**\n\n"
                    "🚀 Instantly turn any file into a shareable link.\n"
                    "**Supports:** Photos, Videos, All File Types up to 4GB!\n"
                    "🔒 Files are stored securely and can be retrieved anytime.\n\n"
                    "**✨ Fast. Premium. Easy.**"
                ),
            )

    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

print("Bot is starting...")
bot.run()
