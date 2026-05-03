from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Viaje, Usuario
from routers.usuarios import get_current_user


def get_viaje_or_404(
    viaje_id: int,
    db: Session = Depends(get_db)
):
    viaje = db.query(Viaje).filter(Viaje.id == viaje_id).first()

    if not viaje:
        raise HTTPException(404, "Viaje no encontrado")

    return viaje


def require_participante(
    viaje: Viaje = Depends(get_viaje_or_404),
    user: Usuario = Depends(get_current_user)
):
    if user.id not in [viaje.cliente_id, viaje.conductor_id]:
        raise HTTPException(403, "No autorizado")

    return viaje


def require_cliente(
    viaje: Viaje = Depends(get_viaje_or_404),
    user: Usuario = Depends(get_current_user)
):
    if user.id != viaje.cliente_id:
        raise HTTPException(403, "Solo el cliente puede hacer esto")

    return viaje


def require_conductor(
    viaje: Viaje = Depends(get_viaje_or_404),
    user: Usuario = Depends(get_current_user)
):
    if user.id != viaje.conductor_id:
        raise HTTPException(403, "Solo el conductor puede hacer esto")

    return viaje