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
            "limit": 5
        }
        
        if location_bias:
        
            center = location_bias.get("circle", {}).get("center", {})
        
            lat = center.get("latitude")
            lng = center.get("longitude")
        
            if lat is not None and lng is not None:
                params["at"] = f"{lat},{lng}"

        print("========== HERE ==========")
        print({
            "q": params["q"],
            "lang": params["lang"],
            "limit": params["limit"],
            "at": params.get("at")
        })
        print("==========================")

        response = requests.get(

            self.AUTOSUGGEST_URL,

            params=params,

            timeout=10

        )

        response.raise_for_status()

        data = response.json()

        resultados = []

        vistos = set()

        for item in data.get("items", []):

            result_type = item.get("resultType")

            if result_type not in (
                "street",
                "place"
            ):
                continue

            nombre = item.get("title", "").strip()
            
            direccion = (
                item.get("address", {})
                    .get("label", "")
                    .strip()
            )
            
            if direccion.startswith(nombre):
                direccion = direccion[len(nombre):].lstrip(" ,-")
            
            clave = (
                nombre.lower(),
                direccion.lower()
            )
            
            if clave in vistos:
                continue
            
            vistos.add(clave)
            
            resultados.append({
            
                "id":
                    item.get("id"),
            
                "name":
                    nombre,
            
                "address":
                    direccion
            
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
