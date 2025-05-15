from dataclasses import dataclass
from environs import Env
from typing import Optional
from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.client.bot import DefaultBotProperties


@dataclass
class TgBot:
    token: str
    admin_ids: list[str]


@dataclass
class Config:
    tg_bot: TgBot


env: Env = Env()

env.read_env()

# Глобальная переменная для хранения экземпляра бота

def load_config(path) -> Config:

    env: Env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env('TELEGRAM_BOT_TOKEN'),
            admin_ids=[]
        )
    )

config: Config = load_config(".env")
bot = Bot(token=config.tg_bot.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
