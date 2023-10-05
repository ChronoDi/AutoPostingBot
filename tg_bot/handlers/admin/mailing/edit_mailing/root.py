from aiogram import Router

from tg_bot.handlers.admin.mailing.edit_mailing import main_menu, change_group, change_date, add_post, remove_post

router: Router = Router()

router.include_router(main_menu.router)
router.include_router(change_group.router)
router.include_router(change_date.router)
router.include_router(add_post.router)
router.include_router(remove_post.router)