"""
Normalizador de consultas para Places.

Convierte abreviaturas comunes de Perú
a su forma completa antes de consultar
al proveedor.
"""

from __future__ import annotations


class QueryNormalizer:

    def __init__(self):

        self.rules = {

            "jr ": "jirón ",

            "jr. ": "jirón ",

            "av ": "avenida ",

            "av. ": "avenida ",

            "psj ": "pasaje ",

            "psje ": "pasaje ",

            "urb ": "urbanización ",

            "urb. ": "urbanización ",

            "mz ": "manzana ",

            "lt ": "lote "
        }

    def normalize(
        self,
        query: str
    ) -> str:

        texto = query.strip().lower()

        for origen, destino in self.rules.items():

            if texto.startswith(origen):

                texto = texto.replace(
                    origen,
                    destino,
                    1
                )

                break

        return texto


query_normalizer = QueryNormalizer()
