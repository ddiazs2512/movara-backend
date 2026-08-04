"""
HERE Reverse Geocoding Adapter.
"""

from __future__ import annotations

import os
import requests

HERE_API_KEY = os.getenv("HERE_API_KEY")

if not HERE_API_KEY:
    raise Exception("HERE_API_KEY no definida")


class HereReverseAdapter:

    REVERSE_URL = (
        "https://revgeocode.search.hereapi.com/v1/revgeocode"
    )

    def reverse_geocode(
        self,
        lat: float,
        lng: float
    ) -> str:

        params = {
            "at": f"{lat},{lng}",
            "lang": "es-PE",
            "apiKey": HERE_API_KEY
        }

        print("========== HERE REVERSE ==========")
        print(params)
        print("==================================")

        response = requests.get(
            self.REVERSE_URL,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        items = data.get("items", [])

        if not items:
            return ""

        return items[0]["address"]["label"]


here_reverse_adapter = HereReverseAdapter()
