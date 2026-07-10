from services.session_token_service import session_token_service
from core.providers.ProviderEngine import provider_engine

from core.places import (
    query_normalizer,
    location_bias_builder
)

class PlacesService:

    def buscar(
        self,
        query: str,
        session_id: str,
        lat: float,
        lng: float
    ):

        query = query_normalizer.normalize(query)

        location_restriction = location_bias_builder.build_restriction(
            lat=lat,
            lng=lng,
            radio=10000
        )
        
        origin = location_bias_builder.build_origin(
            lat=lat,
            lng=lng
        )

        session_token = session_token_service.obtener_session_token(
            session_id
        )
        
        if not session_token:
            raise Exception("Sesión no encontrada")
        
        resultados = provider_engine.places_search(

            query=query,
        
            session_token=session_token,
        
            location_restriction=location_restriction,
        
            origin=origin
        
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
        
places_service = PlacesService()
