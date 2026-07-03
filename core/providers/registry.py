"""
Registro central de Providers de Movara.
"""

from __future__ import annotations

from core.providers.adapters.google_places import (
    google_places_adapter
)
from core.providers.adapters.mapbox_directions import (
    mapbox_directions_adapter
)


class ProviderRegistry:

    def __init__(self):

        self._providers = {}

    def register(
        self,
        name: str,
        provider
    ):

        self._providers[name] = provider

    def get(
        self,
        name: str
    ):

        provider = self._providers.get(name)

        if provider is None:

            raise Exception(
                f"Provider '{name}' no registrado"
            )

        return provider

    def exists(
        self,
        name: str
    ) -> bool:

        return name in self._providers

    def all(self):

        return dict(self._providers)


provider_registry = ProviderRegistry()


# =====================================
# REGISTRO DE PROVIDERS
# =====================================

provider_registry.register(
    "google",
    google_places_adapter
)
provider_registry.register(
    "mapbox",
    mapbox_directions_adapter
)
