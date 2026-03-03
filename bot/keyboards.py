from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


def get_cancel_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отменить опрос")]], resize_keyboard=True
    )


cancel_keyboard = get_cancel_keyboard()
remove_keyboard = ReplyKeyboardRemove()
