from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from tg_bot.config_data import config

Base = declarative_base()
path: str = f'postgresql+asyncpg://{config.database.user}:{config.database.password}' \
            f'@{config.database.host}/{config.database.db_name}'
engine = create_async_engine(url=path, echo=False)
session_maker = async_sessionmaker(engine, expire_on_commit=False)
