"""
Administrador de rutas de Movara.

Único responsable de decidir si una ruta
sale del cache o del ProviderEngine.
"""

from __future__ import annotations

from core.routes import route_cache
from core.providers.ProviderEngine import provider_engine


class RouteManager:

    def get_route(
        self,
        viaje_id: int,
        route_type: str,
        origin_lat: float,
        origin_lng: float,
        destination_lat: float,
        destination_lng: float
    ):

        ruta = route_cache.get(
            viaje_id,
            route_type
        )

        if ruta is not None:

            print(
                f"[ROUTE CACHE HIT] "
                f"viaje={viaje_id} "
                f"tipo={route_type}"
            )

            return ruta

        print(
            f"[ROUTE CACHE MISS] "
            f"viaje={viaje_id} "
            f"tipo={route_type}"
        )

        ruta = provider_engine.get_directions().directions(
            origin_lat=origin_lat,
            origin_lng=origin_lng,
            destination_lat=destination_lat,
            destination_lng=destination_lng
        )
        
        route_cache.save(
            viaje_id=viaje_id,
            route_type=route_type,
            ruta=ruta
        )

        print(
            f"[ROUTE CACHE SAVE] "
            f"viaje={viaje_id} "
            f"tipo={route_type}"
        )
        
        return ruta


route_manager = RouteManager()
