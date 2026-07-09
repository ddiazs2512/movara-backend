from fastapi import APIRouter
from services.places_service import places_service

router = APIRouter(
    prefix="/places",
    tags=["Places"]
)


@router.post("/session")
def crear_sesion():

    return places_service.crear_sesion()


@router.get("/search")
def buscar(
    q: str,
    session_id: str,
    lat: float,
    lng: float
):

    return places_service.buscar(
        query=q,
        session_id=session_id,
        lat=lat,
        lng=lng
    )


@router.get("/detail")
def detalle(
    place_id: str,
    session_id: str
):

    return places_service.detalle(
        place_id,
        session_id
    )
