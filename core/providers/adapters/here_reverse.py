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
        
        # TEMPORAL: para ver exactamente qué devuelve HERE
        print("========== HERE RESPONSE ==========")
        print(items[0])
        print("===================================")
        
        address = items[0].get("address", {})
        
        street = address.get("street", "")
        house = address.get("houseNumber", "")
        district = address.get("district", "")
        city = address.get("city", "")
        label = address.get("label", "")
        
        if street:
        
            direccion = street
        
            if house:
                direccion += f" {house}"
        
            return direccion
        
        if district:
            return district
        
        if city:
            return city
        
        return label


here_reverse_adapter = HereReverseAdapter()
