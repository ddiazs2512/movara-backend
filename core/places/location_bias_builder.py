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

        return {

            "circle": {

                "center": {

                    "latitude": lat,

                    "longitude": lng

                },

                "radius": float(radio)

            }

        }


location_bias_builder = LocationBiasBuilder()
