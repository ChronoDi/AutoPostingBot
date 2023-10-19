from aiogram import Bot

from tg_bot.config_data import config


bot: Bot = Bot(config.tg_bot.token, parse_mode='HTML')
