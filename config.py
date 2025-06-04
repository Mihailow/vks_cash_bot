from aiogram import Bot, Dispatcher, executor, types

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import BotCommand, BotCommandScopeDefault

from apscheduler.schedulers.asyncio import AsyncIOScheduler

telegram_token = ""
is_testing = True

DB_HOST = "localhost"
DB_NAME = "vks_main"
DB_USER = "postgres"
DB_PASS = "postgres"

bot = Bot(token=telegram_token)
dp = Dispatcher(bot, storage=MemoryStorage())
scheduler = AsyncIOScheduler()

last_message = {}
