import asyncio

from data import config


async def check_members():
    while True:
        users = db.get_users()
        print(users)
        for user, membership, s_day, count_msgs  in users:
            print(user, end='')
            if not check_m_day(membership):
                # print('подписка кончилась', membership, end='')
                db.update_m_day(user, '')
                if count_msgs <= 0 and not check_s_day(s_day):
                    # print('больше нет прав')
                    # записываем с какого дня можно будет снова писать
                    await change_rights(user, config.CHANNEL, False, datetime.fromtimestamp(s_day))

        await asyncio.sleep(60)


from datetime import datetime
from loader import dp, db


def check_s_day(day):
    if not day:
        return True
    return datetime.now().timestamp() >= int(day)

def check_m_day(day):
    return not check_s_day(day)

async def change_rights(user: int, chat:int, change: bool, day_end=None):
    await dp.bot.restrict_chat_member(chat, user,
                                      can_send_messages=change,
                                      until_date=day_end)




# s_day = datetime.now().timestamp()
# from time import sleep
# sleep(8)
# print(check_s_day(s_day))
#

