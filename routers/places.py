from fastapi import APIRouter
from services.places_service import places_service

router = APIRouter(
    prefix="/places",
    tags=["Places"]
)


@router.get("/search")
def buscar(
    q: str
):

    return places_service.buscar(q)


@router.get("/detail")
def detalle(
    place_id: str
):

    return {
        "place_id": place_id
    }
