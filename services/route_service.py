import os

from providers.google.directions_provider import (
    obtener_ruta_google
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
    )

    if provider == "google":
        return obtener_ruta_google(
            lat1,
            lng1,
            lat2,
            lng2
        )

    # if provider == "mapbox":
    #     return obtener_ruta_mapbox(
    #         lat1,
    #         lng1,
    #         lat2,
    #         lng2
    #     )

    raise Exception(
        f"Proveedor de rutas no soportado: {provider}"
    )
