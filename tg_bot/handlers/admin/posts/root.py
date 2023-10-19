from aiogram import Router

from tg_bot.handlers.admin.posts import add_post, process_posts

router: Router = Router()

router.include_router(add_post.router)
router.include_router(process_posts.router)