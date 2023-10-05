import os

from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.database.models import Post


async def remove_all_urls_by_post(session: AsyncSession, post: Post):
    for url in post.urls:

        try:
            os.remove(url.url)
        except FileNotFoundError:
            pass

        await session.delete(url)