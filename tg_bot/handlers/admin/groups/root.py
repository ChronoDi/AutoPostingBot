from aiogram import Router

from tg_bot.handlers.admin.groups import process_group, remove_group


router: Router = Router()

router.include_router(remove_group.router)
router.include_router(process_group.router)


