"""
Administrador de Cache de Movara.

Los servicios nunca deben acceder directamente
a Redis o a un diccionario.

Toda lectura y escritura debe pasar por aquí.
"""

from __future__ import annotations

import time
from typing import Any


class CacheManager:

    def __init__(self):

        self._cache: dict[str, tuple[Any, float]] = {}

    def get(self, key: str):

        item = self._cache.get(key)

        if item is None:
            return None

        value, expires_at = item

        if expires_at < time.time():

            del self._cache[key]

            return None

        return value

    def set(
        self,
        key: str,
        value,
        ttl: int
    ):

        self._cache[key] = (
            value,
            time.time() + ttl
        )

    def exists(self, key: str) -> bool:

        return self.get(key) is not None

    def delete(self, key: str):

        self._cache.pop(key, None)

    def clear(self):

        self._cache.clear()


cache_manager = CacheManager()
