from dataclasses import dataclass


@dataclass
class CacheNames:
    GROUPS: str
    ADMINS: str
    POST_GROUPS: str


cache_names = CacheNames(
    GROUPS='groups',
    ADMINS='admins',
    POST_GROUPS='post_groups'
)