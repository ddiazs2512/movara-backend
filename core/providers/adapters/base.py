"""
Clase base para todos los Providers de Movara.

Todos los proveedores deben implementar
únicamente los métodos que soportan.
"""

from __future__ import annotations

from abc import ABC


class ProviderAdapter(ABC):

    def places_search(
        self,
        query: str,
        session_token: str
    ):
        raise NotImplementedError()

    def place_detail(
        self,
        place_id: str,
        session_token: str
    ):
        raise NotImplementedError()

    def reverse_geocode(
        self,
        lat: float,
        lng: float
    ):
        raise NotImplementedError()

    def directions(
        self,
        origin_lat: float,
        origin_lng: float,
        destination_lat: float,
        destination_lng: float
    ):
        raise NotImplementedError()
