import os

from providers.google.directions_provider import (
    obtener_ruta_google
)
from providers.mapbox.directions_provider import (
    obtener_ruta_mapbox
)
from providers.tomtom.directions_provider import (
    obtener_ruta_tomtom
)

# Futuro
# from providers.mapbox.directions_provider import (
#     obtener_ruta_mapbox
# )


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

    if provider == "google":
        return obtener_ruta_google(
            lat1,
            lng1,
            lat2,
            lng2
        )

    elif provider == "mapbox":
        return obtener_ruta_mapbox(
            lat1,
            lng1,
            lat2,
            lng2
        )

    elif provider == "tomtom":

        return obtener_ruta_tomtom(
            lat1,
            lng1,
            lat2,
            lng2
        )

    raise Exception(
        f"Proveedor de rutas no soportado: {provider}"
    )
