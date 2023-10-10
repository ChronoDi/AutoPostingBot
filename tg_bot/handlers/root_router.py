from aiogram import Router

from tg_bot.handlers import admin, commands, user, bots, test2
from tg_bot.meddleware.translator_runner import TranslatorRunnerMiddleware

router = Router()
router.message.middleware(TranslatorRunnerMiddleware())
router.callback_query.middleware(TranslatorRunnerMiddleware())

router.include_router(commands.router)
router.include_router(admin.router)
router.include_router(user.router)
router.include_router(bots.router)

