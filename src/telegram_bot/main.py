import logging
import asyncio
from aiogram import Dispatcher
from config.config import Config, load_config, bot
from handlers import handlers


logging.basicConfig(level=logging.INFO)


async def main() -> None:
    try:
        dp = Dispatcher()
        dp.include_router(handlers.router)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
