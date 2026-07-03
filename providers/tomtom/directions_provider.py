import os
import requests
import polyline


def obtener_ruta_tomtom(
    lat1,
    lng1,
    lat2,
    lng2
):

    token = os.getenv("TOMTOM_API_KEY")

    if not token:
        raise Exception(
            "TOMTOM_API_KEY no configurado"
        )

    url = (
        "https://api.tomtom.com/routing/1/calculateRoute/"
        f"{lat1},{lng1}:{lat2},{lng2}/json"
    )

    params = {
        "key": token,
        "routeType": "fastest",
        "traffic": "true",
        "travelMode": "car",
        "instructionsType": "coded",
        "language": "es-PE"
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    if "routes" not in data:
        return None

    if len(data["routes"]) == 0:
        return None

    route = data["routes"][0]

    summary = route["summary"]

    distancia_metros = int(summary["lengthInMeters"])
    duracion_segundos = int(summary["travelTimeInSeconds"])
    
    # ======================
    # CONVERTIR A POLYLINE
    # ======================
    
    points = []
    
    for p in route["legs"][0]["points"]:
    
        points.append(
            (
                p["latitude"],
                p["longitude"]
            )
        )
    
    polyline_codificada = polyline.encode(points, precision=5)
    
    return {
    
        "distancia_texto":
            f"{round(distancia_metros / 1000, 1)} km",
    
        "distancia_metros":
            distancia_metros,
    
        "duracion_texto":
            f"{round(duracion_segundos / 60)} min",
    
        "duracion_segundos":
            duracion_segundos,
    
        "polyline":
            polyline_codificada
    }
