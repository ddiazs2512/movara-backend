"""
Construye el Location Bias para Google Places.

Permite priorizar resultados cercanos
a una ubicación determinada.
"""

from __future__ import annotations


class LocationBiasBuilder:

    def build(
        self,
        lat: float,
        lng: float,
        radio: int = 30000
    ) -> dict:
    
        return self.build_bias(
            lat=lat,
            lng=lng,
            radio=radio
        )

    def build_bias(
        self,
        lat: float,
        lng: float,
        radio: int
    ) -> dict:
    
        return {
    
            "circle": {
    
                "center": {
    
                    "latitude": lat,
    
                    "longitude": lng
    
                },
    
                "radius": float(radio)
    
            }
    
        }

    def build_restriction(
        self,
        lat: float,
        lng: float,
        radio: int
    ) -> dict:
    
        return {
    
            "circle": {
    
                "center": {
    
                    "latitude": lat,
    
                    "longitude": lng
    
                },
    
                "radius": float(radio)
    
            }
    
        }

    def build_origin(
        self,
        lat: float,
        lng: float
    ) -> dict:
    
        return {
    
            "latitude": lat,
    
            "longitude": lng
    
        }

location_bias_builder = LocationBiasBuilder()
