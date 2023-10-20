from aiogram import Router

from tg_bot.filters.admins import IsAdmin
from tg_bot.handlers.admin import (posts, mailing,
                                   main_mailing, main_posts, mail_chats,
                                   admins, groups, main_groups)

router = Router()
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


router.include_router(admins.router)
router.include_router(main_mailing.router)
router.include_router(main_posts.router)
router.include_router(mail_chats.router)
router.include_router(main_groups.router)
router.include_router(posts.router)
router.include_router(mailing.router)
router.include_router(groups.router)

