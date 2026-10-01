import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiohttp import web

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "8724351999:AAGmh0Bj7hee_Ki6sr8ferV92GD2d39jEBI"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Vaqtinchalik musiqa bazasi (Sarlavha/Xonanda va Telegram file_id)
# Yangi qo'shiq qo'shish uchun shunchaki nomi va file_id sini kiritasiz
MUSIC_DATABASE = {
    "konsta": {
        "title": "Konsta - Poyga",
        "file_id": "CQACAgIAAxkBAAM1Z..." # Shu yerga Telegram'dagi mp3 fayl id'si qo'yiladi
    }
}

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
    await message.answer("Salom! 🎵\n\nMenga qo'shiq nomini yozing yoki audio fayl yuboring (file_id olish uchun)!")

# Agar botga mp3/audio yuborsangiz, u sizga faylning file_id sini beradi (Adminlar uchun)
@dp.message(F.audio)
async def get_audio_file_id(message: types.Message):
    file_id = message.audio.file_id
    title = message.audio.title or "Noma'lum"
    performer = message.audio.performer or "Noma'lum"
    
    await message.reply(
        f"✅ MP3 fayl qabul qilindi!\n\n"
        f"📌 **Sarlavha:** {performer} - {title}\n"
        f"🔑 **file_id:**\n`{file_id}`\n\n"
        f"_(Bu ID ni kodingizdagi MUSIC_DATABASE ga qo'shib qo'yasiz)_",
        parse_mode="Markdown"
    )

# Qidiruv logikasi
@dp.message(F.text)
async def search_music(message: types.Message):
    query = message.text.lower().strip()
    status_msg = await message.answer("🔍 Qidirilmoqda...")
    
    found = False
    for key, song in MUSIC_DATABASE.items():
        if key in query or query in key:
            try:
                # Faylni yuklamasdan, file_id orqali lahzada yuborish
                await message.answer_audio(
                    audio=song["file_id"],
                    caption=f"🎵 {song['title']}\n\n🤖 Bot orqali uzatildi."
                )
                await status_msg.delete()
                found = True
                break
            except Exception as e:
                logging.error(f"Xatolik: {e}")
                await status_msg.edit_text("❌ Faylni yuborishda xatolik yuz berdi.")
                return

    if not found:
        await status_msg.edit_text(
            "❌ Kechirasiz, bu qo'shiq bazadan topilmadi.\n\n"
            "💡 Bazaga qo'shiq qo mef qo'shish uchun botga MP3 fayl yuboring va `file_id` sini oling."
        )

async def main():
    await start_web_server()
    print("Musiqa boti ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())