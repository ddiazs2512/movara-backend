"""
Circuit Breaker genérico para proveedores.

Evita seguir llamando a un proveedor que
está fallando repetidamente.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class CircuitState:

    failures: int = 0

    opened_at: float = 0.0

    state: str = "CLOSED"


class CircuitBreaker:

    FAILURE_THRESHOLD = 3

    RECOVERY_SECONDS = 30

    def __init__(self):

        self._providers = defaultdict(CircuitState)

    def allow(self, provider: str) -> bool:

        circuit = self._providers[provider]

        if circuit.state == "CLOSED":
            return True

        if circuit.state == "OPEN":

            if time.time() - circuit.opened_at >= self.RECOVERY_SECONDS:

                circuit.state = "HALF_OPEN"

                return True

            return False

        # HALF_OPEN

        return True

    def success(self, provider: str):

        self._providers[provider] = CircuitState()

    def failure(self, provider: str):

        circuit = self._providers[provider]

        circuit.failures += 1

        if circuit.failures >= self.FAILURE_THRESHOLD:

            circuit.state = "OPEN"

            circuit.opened_at = time.time()


circuit_breaker = CircuitBreaker()
