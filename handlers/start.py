import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, AdminFilter, Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.exceptions import BadRequest
from glQiwiApi.qiwi.exceptions import QiwiAPIError

from data import config, strings
from .filter_chat import IsGroup, InDB, IsAdminChat
from loader import dp, db, qiwi_p2p_client
from misc.checking_members import check_s_day, change_rights, check_m_day
import datetime

from .states import ChangePer

BAN_S = datetime.timedelta(days=7)
MEMBER_DAYS = datetime.timedelta(days=30)


@dp.message_handler(IsGroup(), AdminFilter())
async def manage_user(message: types.Message):
    pass


@dp.message_handler(Command('get_id'))
async def get_id(message: types.Message):
    await message.answer(message.from_user.id)


@dp.message_handler(IsAdminChat(), Command('cancel'), state='*', )
async def get_id(message: types.Message, state: FSMContext):
    await state.finish()


@dp.message_handler(IsAdminChat(), Command('give'))
async def manage_user(message: types.Message, state: FSMContext):
    try:
        id_user = message.text.split()[1]
        if not db.is_exist_user(id_user):
            await message.answer('неверный айди')

            return
        await dp.bot.get_chat_member(config.CHANNEL, id_user)
        await ChangePer.first()
        await state.update_data(id_user=id_user)
        await message.answer(id_user, reply_markup=change_per_of_user)

    except BadRequest:
        await message.answer('неверный айди')





@dp.message_handler(IsAdminChat(), state=ChangePer.choose_change)
async def manage_user(message: types.Message, state: FSMContext):
    text = message.text
    data = await state.get_data()
    user = data['id_user']
    user, membership, s_day, count_msgs = db.get_user(user)
    if text == strings.GIVE30:
        db.update_m_day(user, (datetime.datetime.now() + MEMBER_DAYS).timestamp())
        await change_rights(user, config.CHANNEL, True, datetime.datetime.fromtimestamp(s_day))
    elif text == strings.TAKE30:
        db.update_m_day(user, '')
        if count_msgs <= 0 and not check_s_day(s_day):
            # записываем с какого дня можно будет снова писать
            await change_rights(user, config.CHANNEL, False, datetime.datetime.fromtimestamp(s_day))
    elif text == strings.GIVE1:
        db.update_one(user, 1)
        await change_rights(user, config.CHANNEL, True)
    elif text == strings.TAKE1:
        if count_msgs <= 0 and not check_s_day(s_day) and not membership:
            # записываем с какого дня можно будет снова писать
            await change_rights(user, config.CHANNEL, False, datetime.datetime.fromtimestamp(s_day))
    elif text == strings.GIVE7:
        db.update_s_day(user, (datetime.datetime.now() - BAN_S).timestamp())
        await change_rights(user, config.CHANNEL, True)
    elif text == strings.SHOW_USER:
        _, membership, s_day, count_msgs = db.get_user(user)
        if membership:
            membership = 'до ' + datetime.datetime.fromtimestamp(membership).strftime(config.FORMAT_DATE)
        else:
            membership = 'Нет'
        s_day = 'доступно' if check_s_day(s_day) else 'недоступно до ' + datetime.datetime.fromtimestamp(
            s_day).strftime(
            config.FORMAT_DATE)
        await message.answer(
            strings.STATUS_TEXT.format(user,
                                       membership,
                                       s_day,
                                       count_msgs))



@dp.message_handler(IsGroup())
async def manage_user(message: types.Message):
    user = message.from_user.id
    # print('handler')
    # print(message.chat.id)
    if not db.is_exist_user(user):
        await message.reply(strings.NEW_USER)
        day_end = datetime.datetime.now() + BAN_S
        db.add_user(identifier=user, s_day_end=day_end.timestamp())
        await change_rights(user, config.CHANNEL, False, BAN_S)
        return

    _, membership, s_day, count_msgs = db.get_user(user)
    if membership == s_day == '' and count_msgs == 0:
        await message.reply(strings.NEW_USER)
        day_end = datetime.datetime.now() + BAN_S
        db.update_s_day(user, (datetime.datetime.now() + BAN_S).timestamp())
        await change_rights(user, config.CHANNEL, False, BAN_S)
        return

    if membership:
        return
    if count_msgs > 0:
        db.update_one(user, -1)
        if count_msgs - 1 == 0:
            await dp.bot.send_message(chat_id=user, text=strings.ONE_MSG)
            if not check_s_day(s_day):
                await change_rights(user, config.CHANNEL, False, s_day)
        return
    # записываем с какого дня можно будет снова писать
    db.update_s_day(user, (datetime.datetime.now() + BAN_S).timestamp())
    await dp.bot.send_message(chat_id=user, text=strings.S_DAY_LIMIT)
    await change_rights(user, config.CHANNEL, False, BAN_S)


from .menu_keyboard import menu_keyboard, check_bill, change_per_of_user


@dp.message_handler()
async def show_menu(message: types.Message):
    user = message.from_user.id
    if not db.is_exist_user(user):
        db.add_user(user)
    await message.answer(strings.WELCOME.format(message.from_user.first_name), reply_markup=menu_keyboard)


async def check_admin(user):
    member = await dp.bot.get_chat_member(config.CHANNEL, user)
    return member.is_chat_admin()


async def making_bill(callback: types.CallbackQuery, product: str, user: int, amount: int):
    expire = datetime.datetime.now() + datetime.timedelta(minutes=4)
    async with qiwi_p2p_client as w:
        try:
            bill = await w.create_p2p_bill(amount=amount,
                                            comment=strings.BILL_COMMENT.format(product, user),
                                            expire_at=expire)
            keyboard = InlineKeyboardMarkup(resize_keyboard=True)
            keyboard.row(InlineKeyboardButton(text=strings.CHECK, callback_data=f'paying_{product}_' + bill.id))

            await callback.message.answer(text=strings.BILL_MESSAGE.format(bill.pay_url), reply_markup=keyboard)
        except QiwiAPIError as err:
            await callback.message.answer(strings.ERROR)
            raise





@dp.callback_query_handler(Text(startswith='paying'), InDB())
async def paying(callback: types.CallbackQuery):
    data = callback.data.split('_')
    bill = data[2]
    product = data[1]
    user = callback.from_user.id
    async with qiwi_p2p_client as w:
        try:
            if await w.check_if_bill_was_paid(await w.get_bill_by_id(bill)):
            # if True:
                if product == '30':
                    # записываем когда кончится подписка
                    db.update_m_day(user, (datetime.datetime.now() + MEMBER_DAYS).timestamp())
                if product == '1':
                    db.update_one(user, 1)
                await change_rights(user, config.CHANNEL, True)
                await callback.message.answer(strings.SUCCESS_BILL)
            else:
                await callback.message.answer(strings.NONE_BILL)
        except QiwiAPIError as err:
            await callback.message.answer(strings.ERROR)
            raise
    await callback.answer()

@dp.callback_query_handler(Text(startswith='buy'), InDB())
async def buying(callback: types.CallbackQuery):
    user = callback.from_user.id
    if await check_admin(user):
        await callback.message.answer('У тебя уже есть все права, так как ты админ группы.')
    else:
        product = callback.data.split('_')[1]
        if product == '30':
            await making_bill(callback, product, user, 1)
        else:
            await making_bill(callback, product, user, 1)

    await callback.answer()


@dp.callback_query_handler(Text(strings.SHOW_STATUS), InDB())
async def status(callback: types.CallbackQuery):
    _, membership, s_day, count_msgs = db.get_user(callback.from_user.id)
    if membership:
        membership = 'до ' + datetime.datetime.fromtimestamp(membership).strftime(config.FORMAT_DATE)
    else:
        membership = 'Нет'
    s_day = 'доступно' if check_s_day(s_day) else 'недоступно до ' + datetime.datetime.fromtimestamp(s_day).strftime(
        config.FORMAT_DATE)
    await callback.message.answer(
        strings.STATUS_TEXT.format(callback.from_user.first_name,
                                   membership,
                                   s_day,
                                   count_msgs))

    await callback.answer()

