import enum
import datetime

from sqlalchemy import JSON
from sqlalchemy import BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tg_bot.database.base import Base


class Role(enum.Enum):
    SUPER_ADMIN = 'super_admin'
    ADMIN = 'admin'
    USER = 'user'


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    first_name: Mapped[str] = mapped_column(nullable=True)
    second_name: Mapped[str] = mapped_column(nullable=True)
    user_name: Mapped[str] = mapped_column(nullable=True)
    role: Mapped['Role'] = mapped_column(nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.datetime.utcnow)


class Post(Base):
    __tablename__ = 'posts'

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    group: Mapped[str] = mapped_column(nullable=False)
    group_id: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    urls: Mapped[list["Url"]] = relationship(back_populates='post',
                                             uselist=True,
                                             cascade='all, delete-orphan',
                                             lazy='selectin')
    text: Mapped[str] = mapped_column(nullable=True)
    post_mailing: Mapped['PostMailing'] = relationship(back_populates='post')

    def __repr__(self) -> str:
        return f'id = {self.id}, group = {self.group}, group_id = {self.group_id}'


class Url(Base):
    __tablename__ = 'urls'

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, autoincrement=True)
    url: Mapped[str] = mapped_column()
    group: Mapped[str] = mapped_column(nullable=False)
    post: Mapped["Post"] = relationship(back_populates='urls', uselist=False)
    post_id: Mapped[str] = mapped_column(ForeignKey('posts.group_id'), unique=False)


class Group(Base):
    __tablename__ = 'groups'

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, primary_key=True)
    type: Mapped[str] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False)


class Mailing(Base):
    __tablename__ = 'malling'

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    count_posts: Mapped[int] = mapped_column(nullable=False, default=0)
    is_sent: Mapped[bool] = mapped_column(nullable=False, default=False)
    task_id: Mapped[int] = mapped_column(unique=False, nullable=True)
    group_id: Mapped[int] = mapped_column(ForeignKey('groups.tg_id'), unique=False)
    mailing_date: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    post_mailing: Mapped['PostMailing'] = relationship(back_populates='mailing')


class PostMailing(Base):
    __tablename__ = 'post_mailing'

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, autoincrement=True)
    post_id: Mapped[int] = mapped_column(ForeignKey('posts.id'))
    mailing_id: Mapped[int] = mapped_column(ForeignKey('malling.id'))
    order: Mapped[int] = mapped_column(nullable=False)
    post: Mapped['Post'] = relationship(back_populates='post_mailing')
    mailing: Mapped['Mailing'] = relationship(back_populates='post_mailing')


class DbSchedule(Base):
    __tablename__ = "taskiq_schedules"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, autoincrement=True)
    task_name:Mapped[str] = mapped_column(nullable=False)
    args = mapped_column(JSON)
    kwargs = mapped_column(JSON)
    labels = mapped_column(JSON)
    time: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

