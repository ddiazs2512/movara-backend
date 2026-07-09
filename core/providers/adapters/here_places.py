"""
HERE Places Adapter.

Único responsable de comunicarse con
HERE Geocoding & Search API.
"""

from __future__ import annotations

import os
import requests

HERE_API_KEY = os.getenv("HERE_API_KEY")

if not HERE_API_KEY:
    raise Exception("HERE_API_KEY no definida")


class HerePlacesAdapter:

    AUTOSUGGEST_URL = (
        "https://autosuggest.search.hereapi.com/v1/autosuggest"
    )

    LOOKUP_URL = (
        "https://lookup.search.hereapi.com/v1/lookup"
    )

    def places_search(
        self,
        query: str,
        session_token: str,
        location_bias: dict | None = None
    ):

        params = {

            "q": query,

            "apiKey": HERE_API_KEY,

            "lang": "es-PE",

            "limit": 10

        }

        response = requests.get(

            self.AUTOSUGGEST_URL,

            params=params,

            timeout=10

        )

        response.raise_for_status()

        data = response.json()

        resultados = []

        for item in data.get("items", []):

            if item.get("resultType") not in (
                "place",
                "locality",
                "street",
                "houseNumber"
            ):
                continue

            resultados.append({

                "id":
                    item.get("id"),

                "name":
                    item.get("title"),

                "address":
                    item.get("address", {})
                        .get("label", "")

            })

        return resultados

    def place_detail(
        self,
        place_id: str,
        session_token: str
    ):

        params = {

            "id": place_id,

            "apiKey": HERE_API_KEY

        }

        response = requests.get(

            self.LOOKUP_URL,

            params=params,

            timeout=10

        )

        response.raise_for_status()

        data = response.json()

        position = data.get("position", {})

        return {

            "id":
                data.get("id"),

            "name":
                data.get("title"),

            "address":
                data.get("address", {})
                    .get("label"),

            "lat":
                position.get("lat"),

            "lng":
                position.get("lng")

        }


here_places_adapter = HerePlacesAdapter()
