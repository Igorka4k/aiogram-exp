from aiogram.types import KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

left_slide_btn = InlineKeyboardButton("<<", callback_data='<<')
right_slide_btn = InlineKeyboardButton(">>", callback_data='>>')
buy_btn = InlineKeyboardButton("Buy", callback_data='buy')
kb1 = InlineKeyboardMarkup().add(left_slide_btn, buy_btn, right_slide_btn)

kb2 = InlineKeyboardMarkup(inline_keyboard=InlineKeyboardButton("123", callback_data='123'))
