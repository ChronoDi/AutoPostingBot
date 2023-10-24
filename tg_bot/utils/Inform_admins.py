from sqlalchemy.ext.asyncio import AsyncSession

from bot import bot
from tg_bot.database.models import User
from tg_bot.utils.database.user import get_admins


async def inform_admins(session: AsyncSession, text: str) -> None:
    admins: list[User] = await get_admins(session)

    for admin in admins:
        await bot.send_message(admin.tg_id, text)
