from aiogram.dispatcher.filters.state import StatesGroup, State


class ChangePer(StatesGroup):
    choose_change = State()
