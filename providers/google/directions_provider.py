import os
import requests


def obtener_ruta_google(
    lat1,
    lng1,
    lat2,
    lng2
):
    API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

    if not API_KEY:
        raise Exception(
            "GOOGLE_MAPS_API_KEY no configurada"
        )

    url = "https://maps.googleapis.com/maps/api/directions/json"

    params = {
        "origin": f"{lat1},{lng1}",
        "destination": f"{lat2},{lng2}",
        "key": API_KEY,
        "mode": "driving"
    }

    response = requests.get(
        url,
        params=params
    )

    data = response.json()

    if data["status"] != "OK":
        return None

    route = data["routes"][0]
    leg = route["legs"][0]

    return {
        "distancia_texto": leg["distance"]["text"],
        "distancia_metros": leg["distance"]["value"],
        "duracion_texto": leg["duration"]["text"],
        "duracion_segundos": leg["duration"]["value"],
        "polyline": route["overview_polyline"]["points"]
    }
