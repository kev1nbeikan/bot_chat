from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from data import config
from data.config import CHANNEL
from loader import db, dp


class IsGroup(BoundFilter):

    async def check(self, message: types.Message):
        return message.chat.id == CHANNEL


class InDB(BoundFilter):

    async def check(self, message: types.Message):
        return db.is_exist_user(message.from_user.id)


class IsAdminChat(BoundFilter):

    async def check(self, message: types.Message):
        member = await dp.bot.get_chat_member(config.CHANNEL, message.from_user.id)
        return member.is_chat_admin()