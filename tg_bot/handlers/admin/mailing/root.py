from aiogram import Router

from tg_bot.handlers.admin.mailing import process_mailing, add_mailing, remove_mailing, edit_mailing

router: Router = Router()

router.include_router(process_mailing.router)
router.include_router(add_mailing.router)
router.include_router(remove_mailing.router)
router.include_router(edit_mailing.router)

