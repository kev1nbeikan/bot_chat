from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from glQiwiApi import QiwiP2PClient

from data import config
from misc.db_api import DB

qiwi_p2p_client = QiwiP2PClient(
    secret_p2p=config.QIWI_TOCKEN)
db = DB()

db.create_table_users()

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
