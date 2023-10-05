from aiogram import Router

from tg_bot.filters.admins import IsAdmin
from tg_bot.handlers.admin import admin_echo, posts, mailing

router = Router()


router.include_router(admin_echo.router)
router.include_router(posts.router)
router.include_router(mailing.router)
