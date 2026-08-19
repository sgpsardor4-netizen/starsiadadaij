import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import config
from bot.database import init_db
from bot.handlers import start, orders, admin, humo_listener, humo_review

logging.basicConfig(level=logging.INFO)


async def main():
    if not config.bot_token:
        raise RuntimeError("BOT_TOKEN .env faylida ko'rsatilmagan!")

    await init_db()

    bot = Bot(token=config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(orders.router)
    dp.include_router(admin.router)
    dp.include_router(humo_review.router)
    dp.include_router(humo_listener.router)

    logging.info("Bot ishga tushdi (polling rejimida)...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
