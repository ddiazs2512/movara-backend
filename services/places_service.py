import os
import requests

GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

if not GOOGLE_PLACES_API_KEY:
    raise Exception("GOOGLE_PLACES_API_KEY no definida")


class PlacesService:

    def buscar(self, query: str):
        raise NotImplementedError()

    def detalle(self, place_id: str):
        raise NotImplementedError()


places_service = PlacesService()
