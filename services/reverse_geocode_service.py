from core.providers.ProviderEngine import provider_engine


class ReverseGeocodeService:

    def obtener_direccion(
        self,
        lat: float,
        lng: float
    ):

        direccion = provider_engine.reverse_geocode(
            lat=lat,
            lng=lng
        )

        return {
            "success": True,
            "address": direccion
        }


reverse_geocode_service = ReverseGeocodeService()
