"""
Google Places Adapter.

Único responsable de comunicarse con
Google Places API.

Ningún otro módulo debe realizar
requests directamente a Google Places.
"""

from __future__ import annotations

import os
import requests

GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

if not GOOGLE_PLACES_API_KEY:
    raise Exception("GOOGLE_PLACES_API_KEY no definida")


class GooglePlacesAdapter:

    AUTOCOMPLETE_URL = (
        "https://places.googleapis.com/v1/places:autocomplete"
    )

    DETAIL_URL = (
        "https://places.googleapis.com/v1/places"
    )

    def places_search(
        self,
        query: str,
        session_token: str
    ):

        headers = {

            "Content-Type": "application/json",

            "X-Goog-Api-Key": GOOGLE_PLACES_API_KEY

        }

        body = {

            "input": query,

            "languageCode": "es",

            "regionCode": "PE",

            "sessionToken": session_token

        }

        response = requests.post(

            self.AUTOCOMPLETE_URL,

            headers=headers,

            json=body,

            timeout=10

        )

        response.raise_for_status()

        data = response.json()

        resultados = []

        for item in data.get("suggestions", []):

            place = item.get("placePrediction")

            if not place:
                continue

            resultados.append({

                "id":
                    place.get("placeId"),

                "name":
                    place.get("text", {})
                        .get("text", ""),

                "address":
                    place.get("structuredFormat", {})
                        .get("secondaryText", {})
                        .get("text", "")

            })

        return resultados

    def place_detail(
        self,
        place_id: str,
        session_token: str
    ):

        headers = {

            "X-Goog-Api-Key": GOOGLE_PLACES_API_KEY,

            "X-Goog-FieldMask":
                "id,displayName,formattedAddress,location"

        }

        url = (
            f"{self.DETAIL_URL}/{place_id}"
            f"?sessionToken={session_token}"
        )

        response = requests.get(

            url,

            headers=headers,

            timeout=10

        )

        response.raise_for_status()

        data = response.json()

        return {

            "id":
                data.get("id"),

            "name":
                data.get("displayName", {})
                    .get("text"),

            "address":
                data.get("formattedAddress"),

            "lat":
                data.get("location", {})
                    .get("latitude"),

            "lng":
                data.get("location", {})
                    .get("longitude")

        }


google_places_adapter = GooglePlacesAdapter()
