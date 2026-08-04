"""
HERE Reverse Geocoding Adapter.

Único responsable de comunicarse con
HERE Reverse Geocoding API.
"""

from __future__ import annotations

import os
import requests


HERE_API_KEY = os.getenv("HERE_API_KEY")

if not HERE_API_KEY:
    raise Exception("HERE_API_KEY no configurado")


class HereReverseAdapter:

    BASE_URL = (
        "https://revgeocode.search.hereapi.com/v1/revgeocode"
    )

    def reverse_geocode(
        self,
        lat: float,
        lng: float
    ) -> str:

        url = (
            f"{self.BASE_URL}"
            f"?at={lat},{lng}"
            f"&lang=es-PE"
            f"&apiKey={HERE_API_KEY}"
        )

        print("========== HERE REVERSE ==========")
        print(url)
        print("=================================")

        response = requests.get(
            url,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        items = data.get("items", [])

        if not items:
            return ""

        return items[0].get(
            "address",
            {}
        ).get(
            "label",
            ""
        )


here_reverse_adapter = HereReverseAdapter()
