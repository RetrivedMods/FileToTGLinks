import os
import json
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant

# Load environment variables
load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
STORAGE_CHAT_ID = int(os.getenv("STORAGE_CHAT_ID"))
REQUIRED_CHANNEL = os.getenv("REQUIRED_CHANNEL")

# Load file database
FILE_DB = {}
if os.path.exists("files.json"):
    with open("files.json", "r") as f:
        FILE_DB = json.load(f)

def save_db():
    with open("files.json", "w") as f:
        json.dump(FILE_DB, f, indent=2)

# Helper to format file size nicely
def format_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = 0
    while size_bytes >= 1024 and i < len(size_name) - 1:
        size_bytes /= 1024
        i += 1
    return f"{size_bytes:.2f} {size_name[i]}"

# Initialize bot
bot = Client("filestreambot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Check if user joined the required channel
async def check_subscription(client, message):
    try:
        user = await client.get_chat_member(REQUIRED_CHANNEL, message.from_user.id)
        return user.status in ("member", "administrator", "creator")
    except UserNotParticipant:
        return False
    except Exception as e:
        print(f"Subscription check error: {e}")
        return False

@bot.on_message(filters.private & filters.command("start"))
async def start_handler(client, message: Message):
    if not await check_subscription(client, message):
        await message.reply_photo(
            photo="https://camo.githubusercontent.com/cc0b6a3547991fa106f7265c07b3793bdea083130f91d68497347a6adc5085f9/68747470733a2f2f74656c656772612e70682f66696c652f3464313234343030623938356232666536656531632e6a7067",
            caption="📢 **Join our official channel to use this bot.**\n\nClick the button below and join, then press /start again.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔗 Join Channel", url=f"https://t.me/{REQUIRED_CHANNEL}")]]
            ),
        )
        return

    args = message.text.split(" ")
    if len(args) == 2:
        file_id = args[1]
        if file_id in FILE_DB:
            file_data = FILE_DB[file_id]
            await message.reply_document(
                file_data["file_id"],
                caption=f"📥 **Here's your file!**\n📁 {file_data['file_name']}",
            )
        else:
            await message.reply_text("❌ File not found or expired.")
        return

    await message.reply_photo(
        photo="https://camo.githubusercontent.com/cc0b6a3547991fa106f7265c07b3793bdea083130f91d68497347a6adc5085f9/68747470733a2f2f74656c656772612e70682f66696c652f3464313234343030623938356232666536656531632e6a7067",
        caption=(
            "👋 **Welcome to FileX Bot!**\n\n"
            "📁 Send me any **file** — document, video, audio, or photo — and I’ll instantly give you a **private shareable link**.\n\n"
            "🔒 Files are safely stored and accessible only by you.\n"
            "⚡️ _Fast. Secure. Premium._"
        ),
    )

@bot.on_message(filters.private & filters.command("help"))
async def help_command(client, message: Message):
    if not await check_subscription(client, message):
        await message.reply_text("❌ You must join our channel to use this bot.")
        return

    await message.reply_text(
        "👋 **How to Use FileX Bot**\n\n"
        "1. Send me any file (photo, document, video, audio).\n"
        "2. I’ll reply with a shareable link.\n"
        "3. Others can use that link to download the file.\n\n"
        "Use /start to return to the main menu."
    )

@bot.on_message(filters.private & (filters.document | filters.video | filters.audio | filters.photo))
async def save_file(client, message: Message):
    if not await check_subscription(client, message):
        await message.reply_text("❌ You must join our channel to use this bot.")
        return

    try:
        sent = await message.forward(STORAGE_CHAT_ID)
        file_id = str(sent.id)

        media = message.document or message.video or message.audio or message.photo
        if isinstance(media, list):  # For photo lists
            media = media[-1]

        file_name = getattr(media, "file_name", None)
        # For photos, file_name often doesn't exist, use unique fallback
        if not file_name:
            file_name = f"file_{file_id}"

        file_size = getattr(media, "file_size", 0)
        file_type = message.media
        file_tg_id = media.file_id

        FILE_DB[file_id] = {
            "file_type": str(file_type),
            "file_id": file_tg_id,
            "file_name": file_name,
            "file_size": file_size,
        }
        save_db()

        bot_username = (await client.get_me()).username
        start_link = f"https://t.me/{bot_username}?start={file_id}"

        await message.reply_text(
            f"📤 **File Uploaded!**\n\n"
            f"📁 Name: `{file_name}`\n"
            f"📏 Size: `{format_size(file_size)}`\n"
            f"📦 Type: `{file_type}`\n"
            f"⚙️ Hash: `{file_id}`\n\n"
            f"🔗 **Share Link:**\n[Click Here]({start_link})",
            disable_web_page_preview=True,
        )

    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

print("Bot is starting...")
bot.run()
