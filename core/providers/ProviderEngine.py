"""
Provider Engine de Movara.

Responsable de entregar el Provider correcto
a cada servicio.

Los servicios nunca deben conocer Google,
Mapbox o cualquier otro proveedor.
"""

from __future__ import annotations

from core.config import (
    PRIMARY_PLACES_PROVIDER,
    PRIMARY_REVERSE_PROVIDER,
    PRIMARY_DIRECTIONS_PROVIDER,
    FALLBACK_PROVIDER
)

from core.providers.registry import (
    provider_registry
)


class ProviderEngine:

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


provider_engine = ProviderEngine()
