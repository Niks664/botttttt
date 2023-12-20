from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import types

def get_keyboard():
    buttons = [
        types.InlineKeyboardButton(text="-100", callback_data="num_decr"),
        types.InlineKeyboardButton(text="+100", callback_data="num_incr"),
        types.InlineKeyboardButton(text="Пополнить", callback_data="num_finish")
    ]

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard
