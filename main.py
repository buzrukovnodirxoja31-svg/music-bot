import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiohttp import web
import yt_dlp

# Logging - Render Logs panelida barcha jarayonlarni aniq ko'rib turish uchun
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "8724351999:AAGmh0Bj7hee_Ki6sr8ferV92GD2d39jEBI"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Render Web Service uchun port ochuvchi soxta server
async def handle(request):
    return web.Response(text="Bot muvaffaqiyatli ishlamoqda!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Salom! 🎵\n\nMenga istalgan qo'shiq nomi yoki xonanda ismini yozing, men uni topib yuboraman!")

@dp.message(F.text)
async def download_music(message: types.Message):
    query = message.text
    status_msg = await message.answer("🔍 Qo'shiq qidirilmoqda, biroz kuting...")
    
    # 1. Downloads papkasini majburiy va xatosiz yaratish
    download_dir = os.path.join(os.getcwd(), "downloads")
    os.makedirs(download_dir, exist_ok=True)
    
    # 2. yt-dlp uchun maksimal darajada xavfsiz va barqaror sozlamalar
    ydl_opts = {
        'format': 'm4a/bestaudio/best',  # FFmpeg talab qilmaydigan eng yaxshi audio format
        'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch1:',
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        # Youtube blokirovkalaridan o'tish uchun brauzer simulyatsiyasi
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    downloaded_file = None
    try:
        loop = asyncio.get_event_loop()
        
        def download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(query, download=True)
                if 'entries' in info and len(info['entries']) > 0:
                    info = info['entries'][0]
                filename = ydl.prepare_filename(info)
                return filename, info.get('title', 'Audio')

        downloaded_file, title = await loop.run_in_executor(None, download)
        
        await status_msg.edit_text("⬆️ Qo'shiq yuklanmoqda...")
        
        # Telegramga audio faylni yuborish
        audio = types.FSInputFile(downloaded_file)
        await message.answer_audio(audio=audio, caption=f"🎵 {title}\n\n🤖 Bot orqali yuklab olindi.")
        await status_msg.delete()
        
    except Exception as e:
        logging.error(f"Yuklab olishda xatolik: {e}")
        await status_msg.edit_text("❌ Qo'shiqni yuklab olishda xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring yoki boshqa nom yozing.")
        
    finally:
        # Fayl yuborilgach yoki xato bersa, xotirani tozalash (o'chirib tashlash)
        if downloaded_file and os.path.exists(downloaded_file):
            try:
                os.remove(downloaded_file)
            except Exception as cleanup_err:
                logging.error(f"Faylni o'chirishda xatolik: {cleanup_err}")

async def main():
    await start_web_server()
    print("Musiqa boti ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())