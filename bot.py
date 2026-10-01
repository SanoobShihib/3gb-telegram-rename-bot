import os
import asyncio
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import Message

load_dotenv()

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]

app = Client(
    "rename_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Store pending rename requests
pending_files = {}


@app.on_message(filters.command("start"))
async def start_handler(client, message: Message):
    await message.reply_text(
        "👋 **3GB Rename Bot**\n\n"
        "📤 ഒരു file അയക്കൂ.\n"
        "✏️ ശേഷം പുതിയ filename നൽകാം.\n\n"
        "Example:\n"
        "`movie.mkv` → `My Movie.mkv`"
    )


@app.on_message(filters.document)
async def document_handler(client, message: Message):
    user_id = message.from_user.id

    file_name = message.document.file_name or "file"

    pending_files[user_id] = {
        "file_id": message.document.file_id,
        "file_name": file_name
    }

    await message.reply_text(
        f"📁 **File:** `{file_name}`\n\n"
        "✏️ ഇനി പുതിയ filename അയക്കൂ.\n"
        "Extension (`.mkv`, `.mp4`, `.zip` etc.) കൂടി വേണമെങ്കിൽ ഉൾപ്പെടുത്താം."
    )


@app.on_message(filters.text & ~filters.command(["start"]))
async def rename_handler(client, message: Message):
    user_id = message.from_user.id

    if user_id not in pending_files:
        return

    new_name = message.text.strip()

    if not new_name:
        await message.reply_text("❌ Filename empty ആകരുത്.")
        return

    old_file = pending_files[user_id]

    # Preserve old extension if user didn't provide one
    old_name = old_file["file_name"]

    if "." in old_name and "." not in new_name:
        extension = old_name.rsplit(".", 1)[1]
        new_name = f"{new_name}.{extension}"

    await message.reply_text(
        f"✅ **Rename requested**\n\n"
        f"Old: `{old_name}`\n"
        f"New: `{new_name}`\n\n"
        "⏳ File processing architecture will handle the actual 3GB transfer."
    )

    del pending_files[user_id]


async def main():
    print("🤖 Rename Bot starting...")
    await app.start()
    print("✅ Bot started successfully!")

    try:
        await asyncio.Event().wait()
    finally:
        await app.stop()


if __name__ == "__main__":
    asyncio.run(main())
