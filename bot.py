import logging
from dotenv import load_dotenv
from os import getenv

from db.sql_init import initialize
from db.queries import db_connect

from aiogram import executor, Bot, Dispatcher, types

from context import *
from db.queries import *
from keyboards import *

load_dotenv('.env')
TOKEN = getenv('TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def welcome(message: types.Message):
    await message.answer(text=welcome_msg)


if __name__ == "__main__":
    # initialize(db_connect())
    executor.start_polling(dp)
