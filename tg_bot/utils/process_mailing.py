import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.database.models import Mailing, Group, Post, PostMailing
from tg_bot.utils.database.group import get_group_by_tg_id
from tg_bot.utils.database.mailing import get_all_mailing, get_mailing_by_id, set_group, set_time, change_post_count, \
    remove_mailing
from tg_bot.utils.database.post import get_post, get_post_by_id
from tg_bot.utils.database.post_mailing import add_post_mailing, get_all_post_in_mailing, get_post_mailing_by_id, \
    get_post_mailing_by_mailing_id_order, commit_post_mailing, get_post_mailing_by_mailing_id_post_id, \
    get_post_mailing_by_mailing_id_post_mailing_id, get_post_higher_order, remove_post
from tg_bot.utils.exceptions import PostExist


async def get_mailing_dict(session: AsyncSession):
    mailing: list[Mailing] = await get_all_mailing(session)
    need_dict: dict[str, str] = {}

    for mail in mailing:
        need_dict.update({str(mail.id) : mail.name})


    return need_dict


async def get_group_name_mailing(session: AsyncSession, mailing_id: int) -> str:
    mailing: Mailing = await get_mailing_by_id(session, mailing_id)

    group: Group = await get_group_by_tg_id(session, mailing.group_id)

    return group.title


async def change_group(session: AsyncSession, mailing_id: int, new_group_id: int):
    await set_group(session, mailing_id, new_group_id)


async def change_date(session: AsyncSession, mailing_id: int, date: datetime):
    await set_time(session, mailing_id, date)


async def get_date(session: AsyncSession, mailing_id: int) -> datetime:
    mailing: Mailing = await get_mailing_by_id(session, mailing_id)

    return mailing.mailing_date


async def add_post_to_mailing(session: AsyncSession, mailing_id: int, group_id: str) -> tuple[str, str]:
    post: Post = await get_post(session, group_id)
    post_mailing: PostMailing = await get_post_mailing_by_mailing_id_post_id(session, mailing_id, post.id)

    if not post_mailing:
        mailing: Mailing = await get_mailing_by_id(session, mailing_id)
        await add_post_mailing(session,
                               mailing_id=mailing.id,
                               post_id=post.id,
                               order=mailing.count_posts + 1)
        await change_post_count(session, mailing_id)

        return mailing.name, post.name

    raise PostExist


async def get_posts_dict(session: AsyncSession, mailing_id: int):
    posts_dict: dict[str, str] = {}
    list_post: list[PostMailing] = await get_all_post_in_mailing(session, mailing_id)

    for post in list_post:
        current_post: Post = await get_post_by_id(session, post_id=post.post_id)

        posts_dict.update({f'{post.id}_up' : '▼'})
        posts_dict.update({str(current_post.id) : f'{current_post.name} ({post.order})'})
        posts_dict.update({f'{post.id}_down': '▲'})

    return posts_dict


async def change_mailing_orders(session: AsyncSession, mailing_id: int,
                                post_id: int, is_increase: bool = True):
    mailing: Mailing = await get_mailing_by_id(session, mailing_id)
    current_post_mailing: PostMailing = await get_post_mailing_by_id(session, post_id)

    if is_increase:
        need_order = current_post_mailing.order + 1 \
            if current_post_mailing.order != mailing.count_posts\
            else current_post_mailing.order
    else:
        need_order = current_post_mailing.order - 1\
            if current_post_mailing.order != 1\
            else current_post_mailing.order

    print(need_order)

    near_post_mailing: PostMailing = await get_post_mailing_by_mailing_id_order(session, mailing_id, need_order)
    current_post_mailing.order, near_post_mailing.order = near_post_mailing.order, current_post_mailing.order
    await commit_post_mailing(session, [current_post_mailing, near_post_mailing])


async def get_posts_remove_dict(session: AsyncSession, mailing_id: int) -> dict[str, str]:
    posts_dict: dict[str, str] = {}
    list_post: list[PostMailing] = await get_all_post_in_mailing(session, mailing_id)

    for post in list_post:
        current_post: Post = await get_post_by_id(session, post_id=post.post_id)

        posts_dict.update({str(post.id): current_post.name})

    return posts_dict


async def remove_post_from_mailing(session: AsyncSession, mailing_id: int,
                                   post_mailing_id: int, post_dict: dict[str, str]) -> None:
    post_mailing: PostMailing = await get_post_mailing_by_mailing_id_post_mailing_id(session, mailing_id,
                                                                                     post_mailing_id)
    list_posts: list[PostMailing] = await get_post_higher_order(session, mailing_id, post_mailing.order)

    if list_posts:
        for post in list_posts:
            post.order = post.order - 1

        await commit_post_mailing(session, list_posts)

    await remove_post(session, post_mailing)
    await change_post_count(session, mailing_id, is_increase=False)
    post_dict.pop(str(post_mailing_id))


async def process_remove_mailing(session: AsyncSession, mailing_id: int, mailing_dict: dict[str, str] = None) -> None:
    list_posts: list[PostMailing] = await get_all_post_in_mailing(session, mailing_id)

    if list_posts:
        for post in list_posts:
            await remove_post(session, post)

    await remove_mailing(session, mailing_id)

    if mailing_dict:
        mailing_dict.pop(str(mailing_id))





