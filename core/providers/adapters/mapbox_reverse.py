"""
Mapbox Reverse Geocoding Adapter.

Único responsable de comunicarse con
Mapbox Geocoding API.
"""

from __future__ import annotations

import os
import requests

MAPBOX_ACCESS_TOKEN = os.getenv("MAPBOX_ACCESS_TOKEN")

if not MAPBOX_ACCESS_TOKEN:
    raise Exception("MAPBOX_ACCESS_TOKEN no configurado")


class MapboxReverseAdapter:

    BASE_URL = (
        "https://api.mapbox.com/geocoding/v5/mapbox.places"
    )

    def reverse_geocode(
        self,
        lat: float,
        lng: float
    ) -> str:

        url = (
            f"{self.BASE_URL}/"
            f"{lng},{lat}.json"
            f"?access_token={MAPBOX_ACCESS_TOKEN}"
            f"&language=es"
            f"&limit=1"
        )

        print("========== MAPBOX REVERSE ==========")
        print(url)
        print("===================================")

        response = requests.get(
            url,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        features = data.get("features", [])

        if not features:
            return ""

        return features[0].get("place_name", "")


mapbox_reverse_adapter = MapboxReverseAdapter()
