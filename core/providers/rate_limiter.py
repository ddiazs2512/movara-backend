"""
Rate Limiter genérico para proveedores.

Controla la cantidad de solicitudes por minuto
para cada proveedor externo.
"""

from __future__ import annotations

import time
from collections import defaultdict, deque

from core.config import MAX_PROVIDER_REQUESTS_PER_MINUTE


class RateLimiter:

    WINDOW_SECONDS = 60

    def __init__(self):

        self._requests = defaultdict(deque)

    def allow(
        self,
        provider: str,
        limit: int = MAX_PROVIDER_REQUESTS_PER_MINUTE
    ) -> bool:

        now = time.time()

        queue = self._requests[provider]

        while queue and now - queue[0] > self.WINDOW_SECONDS:
            queue.popleft()

        if len(queue) >= limit:
            return False

        queue.append(now)

        return True

    def current_usage(
        self,
        provider: str
    ) -> int:

        now = time.time()

        queue = self._requests[provider]

        while queue and now - queue[0] > self.WINDOW_SECONDS:
            queue.popleft()

        return len(queue)

    def reset(
        self,
        provider: str
    ):

        self._requests.pop(provider, None)


rate_limiter = RateLimiter()
