"""
Mapbox Directions Adapter.

Único responsable de comunicarse con
Mapbox Directions API.
"""

from __future__ import annotations

import os
import requests


MAPBOX_ACCESS_TOKEN = os.getenv(
    "MAPBOX_ACCESS_TOKEN"
)


class MapboxDirectionsAdapter:

    DIRECTIONS_URL = (
        "https://api.mapbox.com/directions/v5/mapbox/driving"
    )

    def directions(
        self,
        origin_lat: float,
        origin_lng: float,
        destination_lat: float,
        destination_lng: float
    ):

        if not MAPBOX_ACCESS_TOKEN:
            raise Exception(
                "MAPBOX_ACCESS_TOKEN no configurado"
            )

        url = (
            f"{self.DIRECTIONS_URL}/"
            f"{origin_lng},{origin_lat};"
            f"{destination_lng},{destination_lat}"
        )

        response = requests.get(
            url,
            params={
                "access_token": MAPBOX_ACCESS_TOKEN,
                "overview": "full",
                "geometries": "polyline",
                "steps": "false"
            },
            timeout=10
        )

        print("========== MAPBOX ==========")
        print("URL:", response.url)
        print("============================")

        response.raise_for_status()

        data = response.json()

        if not data.get("routes"):
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


mapbox_directions_adapter = MapboxDirectionsAdapter()
