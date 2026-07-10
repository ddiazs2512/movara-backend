from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Mensaje, Usuario, Viaje
from pydantic import BaseModel

router = APIRouter()

# ======================
# SCHEMA
# ======================

class MensajeRequest(BaseModel):
    viaje_id: int
    emisor_id: int
    mensaje: str


# ======================
# ENVIAR MENSAJE
# ======================

@router.post("/enviar_mensaje")
def enviar_mensaje(data: MensajeRequest, db: Session = Depends(get_db)):

    # 🔹 Validar viaje
    viaje = db.query(Viaje).filter(Viaje.id == data.viaje_id).first()
    if not viaje:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")

    # 🔹 Validar participación
    
    if data.emisor_id not in [viaje.cliente_id, viaje.conductor_id]:
        raise HTTPException(status_code=403, detail="No perteneces a este viaje")

    # 🔹 Validar conductor activo (si aplica)
    emisor = db.query(Usuario).filter(Usuario.id == data.emisor_id).first()
    if emisor and emisor.rol == "Conductor" and not emisor.activo:
        raise HTTPException(status_code=403, detail="Conductor desconectado")

    # 🔹 Determinar receptor real (NO confiar en el cliente)
    if data.emisor_id == viaje.cliente_id:
        receptor_real = viaje.conductor_id
    else:
        receptor_real = viaje.cliente_id

    if not receptor_real:
        raise HTTPException(status_code=400, detail="Receptor inválido")

    # 🔹 Crear mensaje
    nuevo = Mensaje(
        viaje_id=data.viaje_id,
        emisor_id=data.emisor_id,
        receptor_id=receptor_real,
        mensaje=data.mensaje
    )

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    # =========================
# FCM
# =========================

tokens = db.query(FCMToken).filter(
    FCMToken.usuario_id == receptor_real
).all()

for t in tokens:

    enviar_notificacion_data(
        token=t.token,
        data={
            "type": "nuevo_mensaje",
            "viaje_id": str(viaje.id),
            "emisor_id": str(data.emisor_id),
            "title": "Tienes un nuevo mensaje",
            "body": data.mensaje
        }
    )

    return {
        "mensaje": "ok",
        "id": nuevo.id
    }


# ======================
# OBTENER MENSAJES (INCREMENTAL)
# ======================

@router.get("/mensajes/{viaje_id}")
def obtener_mensajes(
    viaje_id: int,
    last_id: int = 0,  # 🔥 clave para no traer todo siempre
    db: Session = Depends(get_db)
):

    # 🔹 Validar viaje
    viaje = db.query(Viaje).filter(Viaje.id == viaje_id).first()
    if not viaje:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")

    mensajes = db.query(Mensaje).filter(
        Mensaje.viaje_id == viaje_id,
        Mensaje.id > last_id
    ).order_by(Mensaje.id.asc()).all()

    return {
        "mensajes": [
            {
                "id": m.id,
                "emisor_id": m.emisor_id,
                "mensaje": m.mensaje,
                "fecha": m.fecha.isoformat() if m.fecha else None
            }
            for m in mensajes
        ]
    }
