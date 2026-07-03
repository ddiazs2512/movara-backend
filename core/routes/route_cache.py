"""
Cache de rutas por viaje.

Garantiza que cada ruta de un viaje
sea solicitada al proveedor una sola vez.
"""

from __future__ import annotations


class RouteCache:

    def __init__(self):

        self._cache = {}

    def get(
        self,
        viaje_id: int,
        route_type: str
    ):

        viaje = self._cache.get(viaje_id)

        if viaje is None:
            return None

        return viaje.get(route_type)

    def save(
        self,
        viaje_id: int,
        route_type: str,
        ruta: dict
    ):

        if viaje_id not in self._cache:

            self._cache[viaje_id] = {}

        self._cache[viaje_id][route_type] = ruta

    def delete(
        self,
        viaje_id: int
    ):

        self._cache.pop(viaje_id, None)

    def exists(
        self,
        viaje_id: int,
        route_type: str
    ) -> bool:

        return self.get(
            viaje_id,
            route_type
        ) is not None


route_cache = RouteCache()
