from asyncio import sleep

from aiogram import Bot
from sqlalchemy.ext.asyncio import async_sessionmaker

from tg_bot.database.models import PostMailing, Post
from tg_bot.utils.database.post import get_post_by_id
from tg_bot.utils.database.post_mailing import get_all_post_in_mailing
from tg_bot.utils.process_mailing import process_remove_mailing
from tg_bot.utils.process_posts import load_post


class Sender:
    def __init__(self, bot: Bot, session_pool: async_sessionmaker):
        self._bot = bot
        self._session_pool = session_pool


    async def send_mailing(self, mailing_id: int, group_id: int) -> None:
        async with self._session_pool() as session:
            list_posts: list[PostMailing] = await get_all_post_in_mailing(session, mailing_id)
            list_media_groups: list[str] = []

            for post in list_posts:
                post: Post = await get_post_by_id(session, post.post_id)
                list_media_groups.append(post.group_id)

            for media_group in list_media_groups:
                await load_post(session, media_id=media_group, bot=self._bot, group_id=group_id)
                await sleep(1)

            await process_remove_mailing(session, mailing_id)


    async def get_session_pool(self) -> async_sessionmaker:
        return self._session_pool



