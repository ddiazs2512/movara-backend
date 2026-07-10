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
        
        # Si todavía no hay ubicación válida,
        # buscar sin restriction ni origin
        if lat == 0.0 or lng == 0.0:

            resultados = self._buscar_provider(
        
                query=query,
        
                session_token=session_token
        
            )
        
            return {
        
                "success": True,
        
                "items": resultados
        
            }
        
        # ==========================
        # Intento 1
        # Restriction 10 km
        # ==========================
        
        resultados = self._buscar_provider(
        
            query=query,
        
            session_token=session_token,
        
            location_restriction=location_restriction,
        
            origin=origin
        
        )
        
        if resultados:
        
            return {
        
                "success": True,
        
                "items": resultados
        
            }
        
        # ==========================
        # Intento 2
        # Restriction 25 km
        # ==========================
        
        location_restriction = location_bias_builder.build_restriction(
        
            lat=lat,
        
            lng=lng,
        
            radio=25000
        
        )
        
        resultados = self._buscar_provider(
        
            query=query,
        
            session_token=session_token,
        
            location_restriction=location_restriction,
        
            origin=origin
        
        )
        
        if resultados:
        
            return {
        
                "success": True,
        
                "items": resultados
        
            }
        
        # ==========================
        # Intento 3
        # Bias 50 km
        # ==========================
        
        location_bias = location_bias_builder.build_bias(
        
            lat=lat,
        
            lng=lng,
        
            radio=50000
        
        )
        
        resultados = self._buscar_provider(
        
            query=query,
        
            session_token=session_token,
        
            location_bias=location_bias,
        
            origin=origin
        
        )
        
        return {
        
            "success": True,
        
            "items": resultados
        
        }

    def _buscar_provider(
        self,
        query: str,
        session_token: str,
        location_bias: dict | None = None,
        location_restriction: dict | None = None,
        origin: dict | None = None
    ):
    
        return provider_engine.places_search(
    
            query=query,
    
            session_token=session_token,
    
            location_bias=location_bias,
    
            location_restriction=location_restriction,
    
            origin=origin
    
        )

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
