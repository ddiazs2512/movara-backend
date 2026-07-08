from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from services.territorio_service import TerritorioService

router = APIRouter(
    prefix="/admin",
    tags=["Territorio"]
)


class AreaOperacionCreate(BaseModel):

    codigo: str

    nombre: str

    descripcion: str = ""

    radio_operacion: int = 18000

    latitud: float

    longitud: float

class AreaOperacionUpdate(BaseModel):

    nombre: str

    descripcion: str = ""

    estado: int

    radio_operacion: int

    latitud: float

    longitud: float


class AsignarDistritoRequest(BaseModel):

    distrito_id: int


@router.get("/areas-operacion")
def listar_areas(

    db: Session = Depends(get_db)

):

    return TerritorioService.listar_areas(db)


@router.post("/areas-operacion")
def crear_area(

    request: AreaOperacionCreate,

    db: Session = Depends(get_db)

):

    existente = next(
        (
            a for a in TerritorioService.listar_areas(db)
            if a.codigo.upper() == request.codigo.upper()
        ),
        None
    )

    if existente:

        raise HTTPException(
            400,
            "El código del área ya existe."
        )

    return TerritorioService.crear_area(

        db,

        request.codigo,

        request.nombre,

        request.descripcion,

        request.radio_operacion,

        request.latitud,

        request.longitud
    )


@router.get("/areas-operacion/{area_id}/distritos")
def listar_distritos(

    area_id: int,

    db: Session = Depends(get_db)

):

    return TerritorioService.listar_distritos_area(

        db,

        area_id
    )


@router.post("/areas-operacion/{area_id}/distritos")
def asignar_distrito(

    area_id: int,

    request: AsignarDistritoRequest,

    db: Session = Depends(get_db)

):

    return TerritorioService.asignar_distrito(

        db,

        area_id,

        request.distrito_id
    )

@router.put("/areas-operacion/{area_id}")
def actualizar_area(

    area_id: int,

    request: AreaOperacionUpdate,

    db: Session = Depends(get_db)

):

    area = TerritorioService.actualizar_area(

        db,

        area_id,

        request.nombre,

        request.descripcion,

        request.estado,

        request.radio_operacion,

        request.latitud,

        request.longitud

    )

    if area is None:

        raise HTTPException(
            404,
            "Área no encontrada."
        )

    return area

@router.delete("/areas-operacion/{area_id}/distritos/{distrito_id}")
def quitar_distrito(

    area_id: int,

    distrito_id: int,

    db: Session = Depends(get_db)

):

    ok = TerritorioService.quitar_distrito(

        db,

        area_id,

        distrito_id

    )

    if not ok:

        raise HTTPException(
            404,
            "Relación no encontrada."
        )

    return {
        "ok": True
    }
