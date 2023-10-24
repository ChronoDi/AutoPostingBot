import os, logging

import aiogram.types
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.database.models import Post
from tg_bot.utils.database.post import get_post, get_post_groups, get_posts_by_group, remove
from tg_bot.utils.database.url import remove_all_urls_by_post
from tg_bot.utils.exceptions import FileNotFound, PostInMailing


async def load_post(session: AsyncSession, media_id: str):
    post = await get_post(session, media_id)
    file_list = []

    for media in post.urls:
        match media.group:
            case 'photo':
                file_list.append(aiogram.types.InputMediaPhoto(media=aiogram.types.FSInputFile(media.url),
                                                               caption=post.text if not file_list else None))
            case 'video' | 'video_note':
                file_list.append(aiogram.types.InputMediaVideo(media=aiogram.types.FSInputFile(media.url),
                                                               caption=post.text if not file_list else None))
            case 'audio':
                file_list.append(aiogram.types.InputMediaAudio(media=aiogram.types.FSInputFile(media.url),
                                                               caption=post.text if not file_list else None))
            case 'document':
                file_list.append(aiogram.types.InputMediaDocument(media=aiogram.types.FSInputFile(media.url),
                                                               caption=post.text if not file_list else None))

    logging.info(f'The post {post.name} has been added uploaded for mailing')
    return file_list, post.text


async def get_post_groups_dict(session: AsyncSession):
    post_groups: list[str] = await get_post_groups(session)
    need_dict: dict[str, str] = {}

    for group in post_groups:
        need_dict.update({group : group})

    return need_dict


async def get_posts_by_group_dict(session: AsyncSession, group: str):
    posts: list[Post] = await get_posts_by_group(session, group)
    need_dict: dict[str, str] = {}

    for post in posts:
        need_dict.update({post.group_id : post.name})


    return need_dict


async def remove_post(session: AsyncSession, group_id: str):
    try:
        post: Post = await get_post(session, group_id)
        await remove_all_urls_by_post(session, post)
        await remove(session, post)
        logging.info(f'The post "{post.name}" has been deleted')
    except IntegrityError:
        logging.error(f'The post is in the mailing list')
        raise PostInMailing


async def check_files(post: Post):
    for media in post.urls:
        if not os.path.exists(media.url):
            logging.error(f'The file {media.url} from the post {post.name} was not found')
            raise FileNotFound(post.name)


