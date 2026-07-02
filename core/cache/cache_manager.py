"""
Administrador de Cache de Movara.

Los servicios nunca deben acceder directamente
a Redis ni a un diccionario.

Toda lectura y escritura debe pasar por aquí.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any


@dataclass
class CacheItem:

    value: Any

    provider: str

    created_at: float

    expires_at: float

    hits: int = 0


class CacheManager:

    def __init__(self):

        self._cache: dict[str, CacheItem] = {}

    def get(self, key: str):

        item = self._cache.get(key)

        if item is None:
            return None

        if item.expires_at < time.time():

            del self._cache[key]

            return None

        item.hits += 1

        return item.value

    def get_item(self, key: str):

        item = self._cache.get(key)

        if item is None:
            return None

        if item.expires_at < time.time():

            del self._cache[key]

            return None

        item.hits += 1

        return item

    def set(
        self,
        key: str,
        value: Any,
        ttl: int,
        provider: str = "memory"
    ):

        now = time.time()

        self._cache[key] = CacheItem(

            value=value,

            provider=provider,

            created_at=now,

            expires_at=now + ttl

        )

    def exists(self, key: str) -> bool:

        return self.get_item(key) is not None

    def delete(self, key: str):

        self._cache.pop(key, None)

    def clear(self):

        self._cache.clear()

    def size(self) -> int:

        return len(self._cache)


cache_manager = CacheManager()
