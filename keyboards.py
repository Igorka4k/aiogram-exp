from aiogram.types import KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

# slider keyboard:
left_slide_btn = InlineKeyboardButton("<<", callback_data='<<')
right_slide_btn = InlineKeyboardButton(">>", callback_data='>>')
buy_btn = InlineKeyboardButton("Buy", callback_data='buy')
slider_kb = InlineKeyboardMarkup().add(left_slide_btn, buy_btn, right_slide_btn)


