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
        session_token: str,
        location_bias: dict | None = None,
        location_restriction: dict | None = None,
        origin: dict | None = None
    ):
    
        provider = self.get_places()
    
        return provider.places_search(

            query=query,
        
            session_token=session_token,
        
            location_bias=location_bias,
        
            location_restriction=location_restriction,
        
            origin=origin
        
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
    
        # =========================
        # CACHE KEY
        # =========================
    
        cache_key = (
            f"reverse:"
            f"{round(lat, 4)}:"
            f"{round(lng, 4)}"
        )
    
        # =========================
        # CACHE HIT
        # =========================
    
        cached = cache_manager.get(cache_key)
    
        if cached is not None:
    
            print(f"[REVERSE CACHE HIT] {cache_key}")
    
            return cached
    
        print(f"[REVERSE CACHE MISS] {cache_key}")
    
        # =========================
        # MAPBOX
        # =========================
    
        provider = self.get_reverse()
    
        direccion = provider.reverse_geocode(
            lat=lat,
            lng=lng
        )
    
        # =========================
        # SAVE CACHE
        # =========================
    
        cache_manager.set(
    
            key=cache_key,
    
            value=direccion,
    
            ttl=60,
    
            provider="mapbox"
    
        )
    
        print(f"[REVERSE CACHE SAVE] {cache_key}")
    
        return direccion

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
