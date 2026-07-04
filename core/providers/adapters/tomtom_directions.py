"""
TomTom Directions Adapter.

Único responsable de comunicarse con
TomTom Routing API.
"""

from __future__ import annotations

import os
import requests
import polyline


TOMTOM_API_KEY = os.getenv("TOMTOM_API_KEY")


class TomTomDirectionsAdapter:

    BASE_URL = (
        "https://api.tomtom.com/routing/1/calculateRoute"
    )

    def directions(
        self,
        origin_lat: float,
        origin_lng: float,
        destination_lat: float,
        destination_lng: float
    ):

        if not TOMTOM_API_KEY:
            raise Exception(
                "TOMTOM_API_KEY no configurado"
            )

        url = (
            f"{self.BASE_URL}/"
            f"{origin_lat},{origin_lng}:"
            f"{destination_lat},{destination_lng}/json"
        )

        response = requests.get(
            url,
            params={
                "key": TOMTOM_API_KEY,
                "routeType": "fastest",
                "traffic": "true",
                "travelMode": "car",
                "instructionsType": "coded",
                "language": "es-PE"
            },
            timeout=10
        )

        print("========== TOMTOM ==========")
        print("URL:", response.url)
        print("============================")

        response.raise_for_status()

        data = response.json()

        if not data.get("routes"):
            return None

        route = data["routes"][0]
        summary = route["summary"]

        distancia_metros = int(
            summary["lengthInMeters"]
        )

        duracion_segundos = int(
            summary["travelTimeInSeconds"]
        )

        points = []

        for p in route["legs"][0]["points"]:

            points.append(
                (
                    p["latitude"],
                    p["longitude"]
                )
            )

        polyline_codificada = polyline.encode(
            points,
            precision=5
        )

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


tomtom_directions_adapter = TomTomDirectionsAdapter()
