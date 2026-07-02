from fastapi import APIRouter

router = APIRouter(
    prefix="/places",
    tags=["Places"]
)


@router.get("/search")
def buscar(
    q: str
):

    return {
        "query": q,
        "items": []
    }


@router.get("/detail")
def detalle(
    place_id: str
):

    return {
        "place_id": place_id
    }
