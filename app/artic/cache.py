from cachetools import TTLCache

from app.config import settings

_cache: TTLCache = TTLCache(
    maxsize=settings.ARTIC_CACHE_MAX_SIZE,
    ttl=settings.ARTIC_CACHE_TTL,
)


def get(key: str) -> dict | None:
    return _cache.get(key)


def set(key: str, value: dict) -> None:
    _cache[key] = value
