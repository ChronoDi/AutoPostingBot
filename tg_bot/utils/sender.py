from asyncio import sleep

from sqlalchemy.ext.asyncio import async_sessionmaker

from bot import bot
from tg_bot.database.base import session_maker
from tg_bot.database.models import PostMailing, Post
from tg_bot.utils.database.post import get_post_by_id
from tg_bot.utils.database.post_mailing import get_all_post_in_mailing
from tg_bot.utils.process_mailing import process_remove_mailing
from tg_bot.utils.process_posts import load_post
from tkq import broker


@broker.task
async def send_mailing(mailing_id: int, group_id: int) -> None:
    session_pool: async_sessionmaker = session_maker

    async with session_pool() as session:
        list_posts: list[PostMailing] = await get_all_post_in_mailing(session, mailing_id)
        list_media_groups: list[str] = []

        for post in list_posts:
            post: Post = await get_post_by_id(session, post.post_id)
            list_media_groups.append(post.group_id)

        for media_group in list_media_groups:
            file_list, post.text = await load_post(session, media_id=media_group)

            if file_list:
                await bot.send_media_group(group_id, media=file_list)
            else:
                await bot.send_message(group_id, text=post.text)

            await sleep(1)

        await process_remove_mailing(session, mailing_id)




