import os
import requests
from services.session_token_service import session_token_service
from core.providers.ProviderEngine import provider_engine
from core.places.query_normalizer import query_normalizer
from core.places import (
    query_normalizer,
    location_bias_builder
)

GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

if not GOOGLE_PLACES_API_KEY:
    raise Exception("GOOGLE_PLACES_API_KEY no definida")


class PlacesService:

    def buscar(
        self,
        query: str,
        session_id: str
    ):

        query = query_normalizer.normalize(query)

        url = "https://places.googleapis.com/v1/places:autocomplete"

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": GOOGLE_PLACES_API_KEY
        }

        session_token = session_token_service.obtener_session_token(
            session_id
        )
        
        if not session_token:
            raise Exception("Sesión no encontrada")
        
        resultados = provider_engine.places_search(
            query,
            session_token
        )
        return {
            "success": True,
            "items": resultados
        }

    def crear_sesion(self):

        session_id = session_token_service.crear()
    
        return {
            "success": True,
            "session_id": session_id
        }

    def detalle(
        self,
        place_id: str,
        session_id: str
    ):

        session_token = session_token_service.obtener_session_token(
            session_id
        )
        
        if not session_token:
            raise Exception("Sesión no encontrada")

        url = (
            f"https://places.googleapis.com/v1/places/{place_id}"
            f"?sessionToken={session_token}"
        )
    
        headers = {
            "X-Goog-Api-Key": GOOGLE_PLACES_API_KEY,
            "X-Goog-FieldMask":
                "id,displayName,formattedAddress,location"
        }
    
        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )
    
        response.raise_for_status()
    
        data = response.json()

        session_token_service.eliminar(session_id)
    
        return {

            "success": True,
        
            "data": {
        
                "id":
                    data.get("id"),
        
                "name":
                    data.get("displayName", {}).get("text"),
        
                "address":
                    data.get("formattedAddress"),
        
                "lat":
                    data.get("location", {}).get("latitude"),
        
                "lng":
                    data.get("location", {}).get("longitude")
        
            }
        
        }

places_service = PlacesService()
