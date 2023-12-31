from aiogram import Router

from tg_bot.handlers.commands import start, menu, admins, id

router = Router()

router.include_router(start.router)
router.include_router(admins.router)
router.include_router(menu.router)
router.include_router(id.router)
