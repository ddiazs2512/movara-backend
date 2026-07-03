import os
import geohash2

from core.cache import cache_manager

from providers.google.directions_provider import (
    obtener_ruta_google
)

from providers.mapbox.directions_provider import (
    obtener_ruta_mapbox
)

from providers.tomtom.directions_provider import (
    obtener_ruta_tomtom
)


def obtener_ruta(
    lat1,
    lng1,
    lat2,
    lng2
):

    provider = os.getenv(
        "ROUTE_PROVIDER",
        "google"
    ).lower()

    origen = geohash2.encode(
        lat1,
        lng1,
        precision=6
    )

    destino = geohash2.encode(
        lat2,
        lng2,
        precision=6
    )

    cache_key = (
        f"route:{provider}:{origen}:{destino}"
    )

    ruta = cache_manager.get(cache_key)

    if ruta is not None:

        print(f"[CACHE HIT] {cache_key}")

        return ruta

    print(f"[CACHE MISS] {cache_key}")

    if provider == "google":

        ruta = obtener_ruta_google(
            lat1,
            lng1,
            lat2,
            lng2
        )

    elif provider == "mapbox":

        ruta = obtener_ruta_mapbox(
            lat1,
            lng1,
            lat2,
            lng2
        )

    elif provider == "tomtom":

        ruta = obtener_ruta_tomtom(
            lat1,
            lng1,
            lat2,
            lng2
        )

    else:

        raise Exception(
            f"Proveedor de rutas no soportado: {provider}"
        )

    if ruta:

        cache_manager.set(
            key=cache_key,
            value=ruta,
            ttl=300,
            provider=provider
        )

    return ruta
