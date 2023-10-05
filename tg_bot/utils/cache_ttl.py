from math import inf
from cachetools import TTLCache

cache_ttl = TTLCache(maxsize=inf, ttl=10.0)