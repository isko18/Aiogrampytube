
from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from pytube import YouTube
from dotenv import load_dotenv
import os
import logging

load_dotenv('.env')

buttons = [
    KeyboardButton('/start'),
    KeyboardButton('/help'),
    KeyboardButton('/video'),
    KeyboardButton('/audio')
]

button = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(*buttons)

bot = Bot(os.environ.get("TOKEN"))
dp = Dispatcher(bot, storage=MemoryStorage())
storage = MemoryStorage()
logging.basicConfig(level=logging.INFO)

def url_valid (url):
    try:
        YouTube(url).streams.first()
        return True
    except:
        return False

@dp.message_handler(commands=['start'])
async def start(message:types.Message):
    await message.answer(f'Здраствуйте {message.from_user.full_name}', reply_markup=button)

class DownloadVideo(StatesGroup):
    download = State()

@dp.message_handler(commands=['video'])
async def video(message:types.Message):
    await message.reply(f'Отправьте ссылку на видео, и я вам скачаю его')
    await DownloadVideo.download.set()

@dp.message_handler(state=DownloadVideo.download)
async def download_video(message:types.Message, state:FSMContext):
    if url_valid( message.text) == True:
        await message.answer("Скачиваем видео")
        yt = YouTube(message.text)
        await message.reply(f'{yt.title}')
        video = yt.streams.filter(progressive=True, file_extension="mp4").order_by('resolution').desc().first().download('video', f"{yt.title}.mp4")

        try:
            await message.answer("Отправляем видео...")
            with open(video, 'rb') as down_video:
                await message.answer_video(down_video)
                os.remove(video)
                
        except:
            await message.answer("Произошла ошибка при скачивании")
            os.remove(video)
    
        await state.finish()
    else:
        await message.reply("Ссылка не действительна, отправьте корректную ссылку!")    

class DownloadAudio(StatesGroup):
    download = State()

@dp.message_handler(commands=['audio'])
async def audio(message:types.Message):
    await message.reply(f'Отправьте ссылку на аудио, и я вам скачаю его')
    await DownloadAudio.download.set()

@dp.message_handler(state=DownloadAudio.download)
async def download_audio(message:types.Message, state:FSMContext):
    if url_valid(message.text) == True:

        await message.answer("Скачиваем аудио...")
        aud_yt = YouTube(message.text)
        await message.reply(f'{aud_yt.title}')
        audio = aud_yt.streams.filter(only_audio=True).first().download('audio', f'{aud_yt.title}.mp3')

        try:
            await message.answer("Отправляем аудио...")
            with open(audio, 'rb') as down_audio:
                await message.answer_audio(down_audio)
                os.remove(audio)
        except:
            await message.answer("Произошла ошибка при скачивании")
            os.remove(audio)
    
        await state.finish()
    else:
        await message.reply("Ссылка не действительна, отправьте корректную ссылку!") 

@dp.message_handler()
async def not_found(message:types.Message):
    await message.reply(f"Я вас не понял, введите /help")


executor.start_polling(dp)


# Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force
# .\venv\Scripts\activate