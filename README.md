# FileToLinks Telegram Bot

**FileToLinks Bot** is a secure and user-friendly Telegram bot that enables you to upload any file and instantly receive a shareable download link. Utilizing Telegram’s robust storage infrastructure, your files are kept safe, private, and always accessible, making file sharing seamless and reliable—right from your Telegram app.

<p align="center">
  <img src="https://img.shields.io/badge/Pyrogram-2.0+-blue?logo=python&logoColor=white" alt="Pyrogram">
  <img src="https://img.shields.io/badge/Telegram%20API-Bot-blue?logo=telegram&logoColor=white" alt="Telegram API">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT license">
  <img src="https://img.shields.io/badge/Deploy-Koyeb-yellow?logo=koyeb" alt="Koyeb">
</p>

---

## Features

- **Universal File Support:** Send any file type—documents, videos, music, APKs, ZIPs, photos, and more.
- **Instant Link Generation:** Instantly receive a Telegram download link for every uploaded file.
- **File Metadata:** Get details like file name, size, and MIME type for each upload.
- **Secure Private Storage:** Files are stored in a private Telegram channel, invisible to the public.
- **Easy Retrieval:** Retrieve any stored file using `/start <file_hash>`.
- **Lightweight & Fast:** Built with minimal dependencies and optimized Python code.
- **User-Friendly Experience:** Intuitive commands and clear help messages.
- **Ready for Hosting:** Deploy easily on [Koyeb](https://www.koyeb.com/) or any cloud platform with minimal setup.
- **Open Source:** MIT-licensed and open to contributions.

---

## Demo

Try the bot on Telegram: [@FileToTGLinksBot](https://t.me/FileToTGLinksBot)

---

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Telegram API credentials: `API_ID` and `API_HASH`
- Bot token from [@BotFather](https://t.me/BotFather)
- A private Telegram channel/chat for file storage (get chat ID)
- Python packages: `pyrogram`, `python-dotenv`
- (Optional) [Koyeb](https://www.koyeb.com/) account for cloud hosting

---

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/RetrivedMods/FileToTGLinks.git
   cd FileToTGLinks
   ```

2. **(Optional) Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create a `.env` file in the project root:**
   ```env
   API_ID=your_api_id
   API_HASH=your_api_hash
   BOT_TOKEN=your_bot_token
   STORAGE_CHAT_ID=your_storage_chat_id
   ```

   See [`.env.example`](.env.example) for a template.

---

### Running the Bot

Start the bot locally:
```bash
python bot.py
```
The bot will begin listening for messages and files.

---

## Usage

- **Upload a file:** Send any file to the bot in a private chat. It will reply with a shareable download link.
- **Retrieve a file:** Use `/start <file_hash>` to fetch a stored file via its hash.
- **Help:** Use `/help` to see all available commands and usage instructions.

---

## Storage & Security

- **Storage:** Uploaded files are forwarded to a designated private Telegram channel for safe storage.
- **Metadata:** File metadata and IDs are saved locally in `files.json` for quick lookup and retrieval.
- **Privacy:** Only you (and authorized users) can access your uploaded files—no public listing.

---

## Hosting on Koyeb

You can easily deploy and host this bot for free on [Koyeb](https://www.koyeb.com/):

1. Fork or clone this repo.
2. Push your forked repo to GitHub.
3. On Koyeb, create a new Python service and connect your repo.
4. Set environment variables (`API_ID`, `API_HASH`, `BOT_TOKEN`, `STORAGE_CHAT_ID`) in the Koyeb dashboard.
5. Deploy!

For detailed steps, check [Koyeb’s Python deployment guide](https://docs.koyeb.com/tutorials/deploy-a-python-app).

---

## Contributing

Contributions, bug reports, and feature suggestions are welcome!

- Open an [issue](https://github.com/RetrivedMods/FileToTGLinks/issues) for bugs or feature requests.
- Submit a [pull request](https://github.com/RetrivedMods/FileToTGLinks/pulls) for improvements.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Donate & Support

If you find this project useful, consider supporting development:

- **Donation:** [retrivedmods.com/donate](https://retrivedmods.neocities.org/donation/)

Your donations help keep the bot running and support further development.

---

## Contact

- **Developer:** [@WClientOwner](https://t.me/WClientOwner)
- **GitHub:** [RetrivedMods/FileToTGLinks](https://github.com/RetrivedMods/FileToTGLinks)

---

<p align="center">
  <a href="https://github.com/pyrogram/pyrogram">
    <img src="https://img.shields.io/badge/Built%20with-Pyrogram-3776AB?logo=python&logoColor=white" alt="Pyrogram"/>
  </a>
  <a href="https://core.telegram.org/bots/api">
    <img src="https://img.shields.io/badge/Telegram%20Bot%20API-5A8DEE?logo=telegram&logoColor=white" alt="Telegram API"/>
  </a>
</p>

_Made with ❤️ using Pyrogram and Telegram Bot API_
