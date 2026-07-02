"""
Provider Manager de Movara.

Los servicios nunca deben llamar directamente
a Google o Mapbox.

Toda integración con proveedores externos
debe pasar por esta clase.
"""

from __future__ import annotations

from core.config import (
    PRIMARY_PLACES_PROVIDER,
    PRIMARY_REVERSE_PROVIDER,
    PRIMARY_DIRECTIONS_PROVIDER,
    FALLBACK_PROVIDER
)


class ProviderManager:

    def __init__(self):

        self.places_provider = PRIMARY_PLACES_PROVIDER

        self.reverse_provider = PRIMARY_REVERSE_PROVIDER

        self.directions_provider = PRIMARY_DIRECTIONS_PROVIDER

        self.fallback_provider = FALLBACK_PROVIDER

    def get_places_provider(self):

        return self.places_provider

    def get_reverse_provider(self):

        return self.reverse_provider

    def get_directions_provider(self):

        return self.directions_provider

    def get_fallback_provider(self):

        return self.fallback_provider


provider_manager = ProviderManager()
