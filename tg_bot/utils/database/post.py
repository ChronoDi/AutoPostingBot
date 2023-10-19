from typing import Union

from sqlalchemy import select, distinct
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from tg_bot.database.models import Url, Post


async def add_text_post(session: AsyncSession, text: str, group_id: str, name_post: str):
    post = Post(group_id=group_id, text=text, group='text', name=name_post)

    session.add(post)
    await session.commit()

def try_get_post(session: Session, media_id: str) -> Union[Post, None]:
    post = session.execute(select(Post).where(Post.group_id == media_id)).scalar_one_or_none()

    return post


async def get_post(session: AsyncSession, group_id: str) -> Union[Post, None]:
    result = await session.execute(select(Post).where(Post.group_id == group_id))
    post = result.scalar_one_or_none()

    return post


def creat_new_post(session: Session, media_id: str, group: str, name_post: str):
    try:
        session.add(Post(group_id=media_id, group=group, name=name_post))
        session.commit()
    except IntegrityError:
        session.rollback()


def add_url(session: Session, post: Post, url: str, group: str):
    new_url = Url(url=url, group=group)
    post.urls.append(new_url)
    session.add(new_url)
    session.commit()


async def add_media_post(session: AsyncSession, url: str, text: str, media_id: str, group: str):
    post = await session.run_sync(try_get_post, media_id)

    if text:
        post.text = text

    if url:
        await session.run_sync(add_url, post, url, group)


async def get_all_posts(session: AsyncSession):
    result = await session.execute(select(Post))
    posts = result.scalars().all()

    return posts


async def get_post_groups(session: AsyncSession) -> list[str]:
    result = await session.execute(select(distinct(Post.group)))
    values = [row[0] for row in result]

    return values


async def get_posts_by_group(session: AsyncSession, group:str):
    result = await session.execute(select(Post).where(Post.group == group))
    posts = result.scalars().all()

    return posts

async def get_post_by_id(session: AsyncSession, post_id: int):
    result = await session.execute(select(Post).where(Post.id == post_id))
    posts = result.scalar_one_or_none()

    return posts


def sync_get_post_by_id(session: Session, post_id: int):
    result = session.execute(select(Post).where(Post.id == post_id))
    posts = result.scalar_one_or_none()

    return posts


async def remove(session: AsyncSession, post: Post):
    await session.delete(post)
    await session.commit()