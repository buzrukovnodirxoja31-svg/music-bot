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

# Render Web Service uchun port ochuvchi soxta server
async def handle(request):
    return web.Response(text="Bot xatosiz va muvaffaqiyatli ishlamoqda!")

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
    await message.answer(
        "Salom! 🎵 Botingiz muvaffaqiyatli ishga tushdi!\n\n"
        "📥 **Qanday ishlatiladi?**\n"
        "1. Menga istalgan MP3 musiqa faylini yuboring.\n"
        "2. Men sizga o'sha musiqaning `file_id` kodini beraman.\n\n"
        "Shu kod orqali Telegram serverlaridagi tayyor musiqalarni tezkor uzatishimiz mumkin!"
    )

# Foydalanuvchi MP3 fayl yuborganida file_id qaytaruvchi qism
@dp.message(F.audio)
async def get_audio_file_id(message: types.Message):
    file_id = message.audio.file_id
    title = message.audio.title or "Noma'lum"
    performer = message.audio.performer or "Noma'lum"
    
    await message.reply(
        f"✅ **MP3 fayl qabul qilindi!**\n\n"
        f"🎵 **Ijrochi / Nomi:** {performer} - {title}\n"
        f"🔑 **Ushbu faylning file_id kodi:**\n`{file_id}`\n\n"
        f"_(Ushbu kodni saqlab qo'ying, bu Telegram xotirasidagi unikal ID)_",
        parse_mode="Markdown"
    )

# Matnli xabarlar uchun javob
@dp.message(F.text)
async def text_handler(message: types.Message):
    await message.answer(
        "Menga MP3 audio fayl yuboring, men sizga uning `file_id` kodini chiqarib beraman! 🎶"
    )

async def main():
    await start_web_server()
    print("Bot muvaffaqiyatli ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())