from aiogram import Router

from tg_bot.handlers.user import user_echo


router = Router()

router.include_router(user_echo.router)

