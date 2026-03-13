import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from bot.config import BOT_TOKEN
from bot.handlers import start, survey, admin, errors

logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(survey.router)
    dp.include_router(admin.router)
    dp.include_router(errors.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
