from sqlalchemy.ext.asyncio import AsyncSession

from bot import bot
from tg_bot.database.models import Mailing, User
from tg_bot.utils.database.user import get_admins


async def inform_admins(session: AsyncSession, mailing: Mailing, msg: str) -> None:
    admins: list[User] = await get_admins(session)
    text: str = f'Рассылка "{mailing.name}" на дату "{mailing.mailing_date}" не отправилась, ' \
                f'так как не были найдены все файлы в посте "{msg}"'

    for admin in admins:
        await bot.send_message(admin.tg_id, text)
