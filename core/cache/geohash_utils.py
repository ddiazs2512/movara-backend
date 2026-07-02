"""
Utilidades de Geohash para Movara.

Toda la aplicación debe utilizar este módulo.

No importar pygeohash directamente desde los servicios.
"""

from __future__ import annotations

import pygeohash

from core.config import GEOHASH_PRECISION


def encode(
    lat: float,
    lng: float,
    precision: int = GEOHASH_PRECISION
) -> str:
    """
    Convierte coordenadas a Geohash.
    """

    return pygeohash.encode(
        lat,
        lng,
        precision=precision
    )


def build_key(
    prefix: str,
    lat: float,
    lng: float,
    precision: int = GEOHASH_PRECISION
) -> str:
    """
    Construye una llave de cache.

    Ejemplo:

    reverse:6gkzwm

    directions:6gkzwm
    """

    return f"{prefix}:{encode(lat, lng, precision)}"


def same_geohash(
    lat1: float,
    lng1: float,
    lat2: float,
    lng2: float,
    precision: int = GEOHASH_PRECISION
) -> bool:
    """
    True si ambos puntos pertenecen
    al mismo bloque Geohash.
    """

    return (
        encode(lat1, lng1, precision)
        ==
        encode(lat2, lng2, precision)
    )
