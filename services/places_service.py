import os
import requests

GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

if not GOOGLE_PLACES_API_KEY:
    raise Exception("GOOGLE_PLACES_API_KEY no definida")


class PlacesService:

    def buscar(self, query: str):

        url = "https://places.googleapis.com/v1/places:autocomplete"

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": GOOGLE_PLACES_API_KEY
        }

        body = {
            "input": query,
            "languageCode": "es",
            "regionCode": "PE"
        }

        response = requests.post(
            url,
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

                "place_id":
                    place.get("placeId"),

                "titulo":
                    place.get("text", {}).get("text", ""),

                "direccion":
                    place.get("structuredFormat", {})
                        .get("secondaryText", {})
                        .get("text", "")

            })

        return resultados

    def detalle(self, place_id: str):
        raise NotImplementedError()


places_service = PlacesService()
