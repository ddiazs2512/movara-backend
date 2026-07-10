from fastapi import APIRouter

from services.reverse_geocode_service import (
    reverse_geocode_service
)

router = APIRouter()


@router.get("/reverse_geocode")
def reverse_geocode(
    lat: float,
    lng: float
):

    return reverse_geocode_service.obtener_direccion(
        lat=lat,
        lng=lng
    )
