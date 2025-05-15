import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.bot import DefaultBotProperties
from config.config import Config, load_config
from handlers import handlers


logging.basicConfig(level=logging.INFO)


async def main() -> None:
    config: Config = load_config(".env")
    async with Bot(token=config.tg_bot.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML)) as bot:
        dp = Dispatcher()

        dp.include_router(handlers.router)

        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
