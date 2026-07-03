"""
Provider Engine de Movara.

Único punto de entrada hacia proveedores externos.

Responsabilidades:

- Seleccionar Provider
- Cache
- Rate Limit
- Circuit Breaker
- Analytics
- Retry
- Fallback

Los servicios nunca deben llamar directamente
a Google, Mapbox o cualquier otro proveedor.
"""

from __future__ import annotations

from core.config import (
    PRIMARY_PLACES_PROVIDER,
    PRIMARY_REVERSE_PROVIDER,
    PRIMARY_DIRECTIONS_PROVIDER,
    FALLBACK_PROVIDER
)

from core.providers.registry import provider_registry

from core.cache.cache_manager import cache_manager
from core.providers.rate_limiter import rate_limiter
from core.providers.circuit_breaker import circuit_breaker


class ProviderEngine:

    # ======================================
    # PROVIDERS
    # ======================================

    def get_places(self):

        return provider_registry.get(
            PRIMARY_PLACES_PROVIDER
        )

    def get_reverse(self):

        return provider_registry.get(
            PRIMARY_REVERSE_PROVIDER
        )

    def get_directions(self):

        return provider_registry.get(
            PRIMARY_DIRECTIONS_PROVIDER
        )

    def get_fallback(self):

        return provider_registry.get(
            FALLBACK_PROVIDER
        )

    # ======================================
    # PLACES
    # ======================================

    def places_search(
        self,
        query: str,
        session_token: str
    ):

        provider = self.get_places()

        return provider.places_search(
            query,
            session_token
        )

    def place_detail(
        self,
        place_id: str,
        session_token: str
    ):

        provider = self.get_places()

        return provider.place_detail(
            place_id,
            session_token
        )

    # ======================================
    # REVERSE
    # ======================================

    def reverse_geocode(
        self,
        lat: float,
        lng: float
    ):

        raise NotImplementedError()

    # ======================================
    # DIRECTIONS
    # ======================================

    def directions(
        self,
        origin_lat: float,
        origin_lng: float,
        destination_lat: float,
        destination_lng: float
    ):

        raise NotImplementedError()


provider_engine = ProviderEngine()
