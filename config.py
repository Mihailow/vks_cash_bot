from aiogram import Bot, Dispatcher, executor, types

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

from apscheduler.schedulers.asyncio import AsyncIOScheduler

telegram_token = "6353026522:AAH6nwB6AgNQKQaUwT9PFvfI-8vA7NuYwlY"
is_testing = True

# telegram_token = "6884398594:AAHrVPqEFwX7aTtkEuZolDi5W-c-bHZN0Hk"
# is_testing = False

DB_HOST = "localhost"
DB_NAME = "vks_main"
DB_USER = "postgres"
DB_PASS = "postgres"

bot = Bot(token=telegram_token)
dp = Dispatcher(bot, storage=MemoryStorage())
scheduler = AsyncIOScheduler()

last_message = {}
