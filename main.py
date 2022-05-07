import logging
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, \
    InlineKeyboardMarkup, InlineKeyboardButton
from os import getenv
from keyboards import *
from context import *
from aiogram import Bot, Dispatcher, executor, types

TOKEN = getenv("TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    chat_id = message.chat.id
    await message.answer(welcome_msg)


@dp.message_handler(commands='1')
async def process_command_1(message: types.Message):
    chat_id = message.chat.id
    await bot.send_message(chat_id=chat_id,
                           text="Выбери раздел 1/3",
                           reply_markup=kb1)


@dp.message_handler(commands='2')
async def process_command_2(message: types.Message):
    chat_id = message.chat.id
    await bot.send_message(chat_id=chat_id,
                           text="Теперь выбери кнопку",
                           reply_markup=kb2)


@dp.callback_query_handler(lambda x: x.data == '123')
async def process_callback_poop(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Poop!!')


@dp.callback_query_handler(lambda x: x.data == '<<')
async def process_callback_left_slide(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    text = callback_query.message.text.split()[-1]
    if text == '1/3':
        await callback_query.message.edit_text('Выберите раздел 3/3', reply_markup=kb1)
    elif text == '2/3':
        await callback_query.message.edit_text("Выберите раздел 1/3", reply_markup=kb1)
    elif text == '3/3':
        await callback_query.message.edit_text("Выберите раздел 2/3", reply_markup=kb1)

    # await bot.send_message(callback_query.from_user.id, 'Слайд влево')


@dp.callback_query_handler(lambda x: x.data == '>>')
async def process_callback_right_slide(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    text = callback_query.message.text.split()[-1]
    if text == '1/3':
        await callback_query.message.edit_text('Выберите раздел 2/3', reply_markup=kb1)
    elif text == '2/3':
        await callback_query.message.edit_text("Выберите раздел 3/3", reply_markup=kb1)
    elif text == '3/3':
        await callback_query.message.edit_text("Выберите раздел 1/3", reply_markup=kb1)


@dp.callback_query_handler(lambda x: x.data == 'buy')
async def process_callback_buy(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.message.chat.id
    await callback_query.message.delete()
    await bot.send_message(chat_id=chat_id, text="Купить пока нельзя")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
