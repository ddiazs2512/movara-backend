import os
import requests
from services.session_token_service import session_token_service
from core.providers.ProviderEngine import provider_engine

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

        location_bias = location_bias_builder.build(
            lat=-12.0464,
            lng=-77.0428,
            radio=30000
        )

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
            query=query,
            session_token=session_token,
            location_bias=location_bias
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
    
        data = provider_engine.place_detail(
            place_id=place_id,
            session_token=session_token
        )
    
        session_token_service.eliminar(session_id)
    
        return {
    
            "success": True,
    
            "data": data
    
        }
