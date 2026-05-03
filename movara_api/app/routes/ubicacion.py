from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.usuario import Usuario


router = APIRouter()


# ==============================
# CONEXIÓN DB
# ==============================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ==============================
# ACTUALIZAR UBICACIÓN CONDUCTOR
# ==============================

@router.post("/actualizar_ubicacion")

def actualizar_ubicacion(data: dict, db: Session = Depends(get_db)):

    conductor = db.query(Usuario).filter(
        Usuario.id == data["conductor_id"]
    ).first()

    if not conductor:

        raise HTTPException(
            status_code=404,
            detail="Conductor no encontrado"
        )

    conductor.latitud = data["lat"]

    conductor.longitud = data["lng"]

    db.commit()

    return {
        "mensaje": "ubicacion actualizada"
    }