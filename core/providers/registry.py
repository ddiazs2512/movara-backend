"""
Registro central de Providers de Movara.

Permite registrar y obtener adaptadores
sin que los servicios conozcan su implementación.
"""

from __future__ import annotations


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
