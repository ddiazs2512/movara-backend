import os
import requests


def obtener_ruta_mapbox(
    lat1,
    lng1,
    lat2,
    lng2
):

    token = os.getenv("MAPBOX_ACCESS_TOKEN")

    if not token:
        raise Exception(
            "MAPBOX_ACCESS_TOKEN no configurado"
        )

    url = (
        f"https://api.mapbox.com/directions/v5/mapbox/driving/"
        f"{lng1},{lat1};{lng2},{lat2}"
    )

    params = {
        "access_token": token,
        "overview": "full",
        "geometries": "polyline",
        "steps": "false"
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    print("========== RUTA ==========")
    print("Distancia:", route["distance"])
    print("Duración:", route["duration"])
    print("Geometry inicio:", route["geometry"][:80])
    print("==========================")

    data = response.json()

    if "routes" not in data:
        return None

    if len(data["routes"]) == 0:
        return None

    route = data["routes"][0]

    distancia_metros = int(route["distance"])
    duracion_segundos = int(route["duration"])

    return {
        "distancia_texto": f"{round(distancia_metros / 1000, 1)} km",
        "distancia_metros": distancia_metros,
        "duracion_texto": f"{round(duracion_segundos / 60)} min",
        "duracion_segundos": duracion_segundos,
        "polyline": route["geometry"]
    }
