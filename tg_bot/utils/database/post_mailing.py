from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from tg_bot.database.models import PostMailing
from tg_bot.utils.exceptions import PostExist, PostNotFound


async def add_post_mailing(session: AsyncSession, mailing_id: int, post_id: int, order: int):
    post_mailing: PostMailing = PostMailing(
        post_id=post_id,
        mailing_id=mailing_id,
        order=order
    )

    session.add(post_mailing)
    await session.commit()


async def get_all_post_in_mailing(session: AsyncSession, mailing_id: int):
    result = await session.execute(select(PostMailing)
                                   .where(PostMailing.mailing_id == mailing_id)
                                   .order_by(PostMailing.order))
    list_posts = result.scalars().all()

    return list_posts


async def get_post_mailing_by_id(session: AsyncSession, post_id: int):
    result = await session.execute(select(PostMailing).where(PostMailing.id == post_id))
    post_mailing: PostMailing = result.scalar_one_or_none()

    return post_mailing

async def get_post_mailing_by_mailing_id_order(session: AsyncSession, mailing_id: int, order: int):
    result = await session.execute(select(PostMailing).where(and_(PostMailing.mailing_id == mailing_id,
                                                                  PostMailing.order == order)))
    post_mailing: PostMailing = result.scalar_one_or_none()

    return post_mailing


async def commit_post_mailing(session: AsyncSession, post_mailing: list[PostMailing]):
    for post in post_mailing:
        session.add(post)

    await session.commit()


async def get_post_mailing_by_mailing_id_post_id(session: AsyncSession, mailing_id: int, post_id: int):
    result = await session.execute(select(PostMailing).where(and_(PostMailing.mailing_id == mailing_id,
                                                                  PostMailing.post_id == post_id)))
    post_mailing: PostMailing = result.scalar_one_or_none()

    return post_mailing


async def remove_post(session: AsyncSession, post_mailing: PostMailing) -> None:
    await session.delete(post_mailing)
    await session.commit()


async def get_post_mailing_by_mailing_id_post_mailing_id(session: AsyncSession, mailing_id: int, post_mailing_id: int)\
        -> PostMailing:
    result = await session.execute(select(PostMailing).where(and_(PostMailing.mailing_id == mailing_id,
                                                                  PostMailing.id == post_mailing_id)))
    post_mailing: PostMailing = result.scalar_one_or_none()

    if post_mailing:
        return post_mailing

    raise PostNotFound


async def get_post_higher_order(session: AsyncSession, mailing_id: int, start_order: int):
    result = await session.execute(select(PostMailing).where(and_(PostMailing.mailing_id == mailing_id,
                                                                  PostMailing.order > start_order)))
    list_posts = result.scalars().all()

    return list_posts


def sync_remove_post_mailing(session: Session, mailing_id: int):
    list_posts = session.execute(select(PostMailing).
                                 where(PostMailing.mailing_id == mailing_id)).scalars().all()

    [session.delete(post) for post in list_posts]
    session.commit()


def sync_get_all_post_in_mailing(session: Session, mailing_id: int):
    result = session.execute(select(PostMailing)
                                   .where(PostMailing.mailing_id == mailing_id)
                                   .order_by(PostMailing.order))
    list_posts = result.scalars().all()

    return list_posts