import asyncio
import datetime
from asyncio import sleep
from datetime import timedelta

import pytz
from sqlalchemy.ext.asyncio import async_sessionmaker

from bot import bot
from tg_bot.database.base import session_maker
from tg_bot.database.models import PostMailing, Post, Mailing
from tg_bot.utils.database.mailing import get_mailing_by_id
from tg_bot.utils.database.post import get_post_by_id
from tg_bot.utils.database.post_mailing import get_all_post_in_mailing
from tg_bot.utils.process_mailing import process_remove_mailing, remove_posts_from_mailing, sync_get_list_media_group, \
    check_sending
from tg_bot.utils.process_posts import load_post
from tkq import broker

# Закрываю функцию, пока не станет понятна проблема с двойной отправкой рассылки.
# @broker.task()
# async def send_mailing(mailing_id: int) -> None:
#     session_pool: async_sessionmaker = session_maker
#
#     async with session_pool() as session:
#         mailing: Mailing = await get_mailing_by_id(session, mailing_id)
#
#         if mailing:
#             list_posts: list[PostMailing] = await get_all_post_in_mailing(session, mailing_id)
#             list_media_groups: list[str] = []
#
#             for post in list_posts:
#                 post: Post = await get_post_by_id(session, post.post_id)
#                 list_media_groups.append(post.group_id)
#
#             for media_group in list_media_groups:
#                 file_list = []
#                 text = ''
#                 file_list, text = await load_post(session, media_id=media_group)
#
#                 if file_list:
#                     await bot.send_media_group(mailing.group_id, media=file_list)
#                 else:
#                     await bot.send_message(mailing.group_id, text=text)
#
#                 await sleep(1)
#
#             await process_remove_mailing(session, mailing_id)

@broker.task()
async def send_mailing(mailing_id: int) -> None:
    session_pool: async_sessionmaker = session_maker

    async with session_pool() as session:
        mailing: Mailing = await session.run_sync(check_sending, mailing_id)

        if mailing:
            if mailing.mailing_date + timedelta(minutes=20) >= datetime.datetime.now():
                list_posts: list[PostMailing] = await get_all_post_in_mailing(session, mailing_id)
                list_media_groups: list[str] = []

                for post in list_posts:
                    post: Post = await get_post_by_id(session, post.post_id)
                    list_media_groups.append(post.group_id)

                for media_group in list_media_groups:
                    file_list = []
                    text = ''
                    file_list, text = await load_post(session, media_id=media_group)

                    if file_list:
                        await bot.send_media_group(mailing.group_id, media=file_list)
                    else:
                        await bot.send_message(mailing.group_id, text=text)

                    await sleep(1)

            await process_remove_mailing(session, mailing_id)
