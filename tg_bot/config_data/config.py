from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    token: str
    super_admin: list[int]


@dataclass
class Redis:
    is_need: bool
    host: str
    port: int
    user: str
    password: str
    db: int


@dataclass
class DataBase:
    host: str
    port: int
    user: str
    password: str
    db_name: str


@dataclass
class Path:
    media: str


@dataclass
class Nats:
    host: str
    port: int


@dataclass
class Config:
    tg_bot: TgBot
    redis: Redis
    nats: Nats
    database: DataBase
    paths: Path


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)

    return Config(tg_bot=TgBot(token=env('BOT_TOKEN'),
                               super_admin=list(map(int, env.list('SUPER_ADMIN')))),
                  redis=Redis(host=env('REDIS_HOST'),
                              is_need=env.bool('USE_REDIS'),
                              port=env.int('REDIS_PORT'),
                              password=env.str('REDIS_PASSWORD'),
                              user=env.str('REDIS_USER'),
                              db=env.int('REDIS_BD')),
                  nats=Nats(host=env('NATS_HOST'),
                            port=env.int('NATS_PORT')),
                  database=DataBase(host=env('DB_HOST'),
                                    port=env.int('DB_PORT'),
                                    user=env('DB_USER'),
                                    password=env('DB_PASSWORD'),
                                    db_name=env('DB_NAME')),
                  paths = Path(media=env('MEDIA_PATH')))
