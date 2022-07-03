from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from data import strings

menu_keyboard = InlineKeyboardMarkup(resize_keyboard=True)
menu_keyboard.row(InlineKeyboardButton(strings.BUY_30, callback_data=strings.BUY_30_CALL), InlineKeyboardButton(
    strings.BUY_1, callback_data=strings.BUY_1_CALL))
menu_keyboard.row(InlineKeyboardButton(strings.ADMIN_CHAT, url=strings.ADMIN_CHAT_URL), InlineKeyboardButton(
    strings.STATUS, callback_data=strings.SHOW_STATUS))


check_bill = InlineKeyboardMarkup(resize_keyboard=True)

change_per_of_user = ReplyKeyboardMarkup(resize_keyboard=True)
change_per_of_user.row(strings.GIVE30, strings.TAKE30)
change_per_of_user.row(strings.GIVE1, strings.TAKE1)
change_per_of_user.row(strings.GIVE7, strings.SHOW_USER)