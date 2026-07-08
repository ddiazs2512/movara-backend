from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Configuracion

router = APIRouter(
    prefix="/admin",
    tags=["Administración"]
)


@router.get("/configuracion")
def obtener_configuracion(
    db: Session = Depends(get_db)
):

    configuraciones = (
        db.query(Configuracion)
        .order_by(
            Configuracion.grupo,
            Configuracion.clave
        )
        .all()
    )

    return configuraciones
