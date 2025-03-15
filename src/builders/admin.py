from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu() -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="Geo"),KeyboardButton(text="Cancel")],
        [KeyboardButton(text="Get Token"),KeyboardButton(text="Set token")],
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return keyboard