import asyncio
import os
import yt_dlp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart

# <<< TOKENINGIZNI SHU YERGA QO'YING >>>
API_TOKEN = '8724351999:AAGmh0Bj7hee_Ki6sr8ferV92GD2d39jEBI'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# YouTube'dan MP3 formatida yuklab olish funksiyasi
def download_music(query: str):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'default_search': 'ytsearch1:',
        'quiet': True,
        'noplaylist': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=True)
        if 'entries' in info:
            info = info['entries'][0]
        
        filename = ydl.prepare_filename(info)
        base, _ = os.path.splitext(filename)
        mp3_file = base + ".mp3"
        
        return mp3_file, info.get('title', 'Musiqa')

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(
        f"Salom {message.from_user.first_name}! 🎵\n\n"
        f"Menga **istalgan qo'shiq nomi** yoki xonanda ismini yozing, men uni topib MP3 shaklida yuboraman!",
        parse_mode="Markdown"
    )

@dp.message(F.text)
async def handle_search(message: types.Message):
    song_name = message.text
    status_msg = await message.answer(f"🔍 **'{song_name}'** internetdan qidirilmoqda, biroz kuting...", parse_mode="Markdown")

    try:
        loop = asyncio.get_event_loop()
        file_path, title = await loop.run_in_executor(None, download_music, song_name)

        audio_file = types.FSInputFile(file_path)
        await message.answer_audio(
            audio=audio_file,
            caption=f"🎶 **{title}**\n\n@my_first_test_2009_bot orqali yuklandi.",
            parse_mode="Markdown"
        )

        await status_msg.delete()
        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as e:
        print(f"Xatolik: {e}")
        await status_msg.edit_text(f"😔 Kechirasiz, **'{song_name}'** bo'yicha musiqa topilmadi.")

async def main():
    print("Musiqa boti ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())