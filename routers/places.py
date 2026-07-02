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
    session_id: str
):

    return places_service.buscar(
        q,
        session_id
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
