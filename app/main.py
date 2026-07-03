import os
import re
import asyncio
import traceback

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
from yt_dlp import YoutubeDL

from config import BOT_TOKEN, PROXY

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def download_audio(url: str):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s"),
        "quiet": True,
        "noplaylist": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    # Proxy faqat mavjud bo'lsa qo'shiladi
    if PROXY:
        ydl_opts["proxy"] = PROXY

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

        filename = ydl.prepare_filename(info)
        mp3_file = os.path.splitext(filename)[0] + ".mp3"

        return mp3_file


@dp.message(
    F.text.regexp(r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/")
)
async def youtube_handler(message: Message):
    url = message.text.strip()

    status = await message.answer("⏬ Audio yuklanmoqda...")

    try:
        # Audio yuklash
        file_path = await asyncio.to_thread(download_audio, url)

        print(f"File: {file_path}")
        print(f"Exists: {os.path.exists(file_path)}")

        if not os.path.exists(file_path):
            raise FileNotFoundError("MP3 fayl topilmadi!")

        print(f"Size: {os.path.getsize(file_path)} bytes")

        audio = FSInputFile(file_path)

        # Telegramga yuborish
        await bot.send_audio(
            chat_id=message.chat.id,
            audio=audio,
            caption="✅ Tayyor!"
        )

        await status.delete()

    except Exception:
        traceback.print_exc()
        await status.edit_text("❌ Xatolik yuz berdi. Konsolni tekshiring.")

    finally:
        if 'file_path' in locals() and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass

@dp.message()
async def other(message: Message):
    await message.answer("🎵 YouTube video linkini yuboring.")


async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())