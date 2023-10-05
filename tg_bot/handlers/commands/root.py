from aiogram import Router

from tg_bot.handlers.commands import start, chats, posts, menu, mailing


router = Router()

router.include_router(start.router)
router.include_router(menu.router)
router.include_router(chats.router)
router.include_router(posts.router)
router.include_router(mailing.router)