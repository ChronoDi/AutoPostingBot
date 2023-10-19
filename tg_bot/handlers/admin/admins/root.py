from aiogram import Router

from tg_bot.filters.admins import IsSuperAdmin
from tg_bot.handlers.admin.admins import process_admin, add_admin


router:Router = Router()
router.message.filter(IsSuperAdmin())
router.callback_query.filter(IsSuperAdmin())


router.include_router(process_admin.router)
router.include_router(add_admin.router)