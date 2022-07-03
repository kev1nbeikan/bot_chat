import asyncio

from data import config, strings
from misc.checking_members import check_members
from aiogram import Dispatcher
async def on_startup(dp: Dispatcher):
    asyncio.create_task(check_members())
    try:
        await dp.bot.send_message(config.CHANNEL, "Бот👁 Запущен и готов к работе\n" + strings.START_BOT)

    except Exception as err:
       print(err)


if __name__ == '__main__':
    import datetime
    from aiogram import executor
    from handlers import dp
    today = datetime.date.today().strftime('')
    executor.start_polling(dp, on_startup=on_startup)




