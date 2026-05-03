from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.viaje import Viaje
from app.models.oferta import Oferta
from app.models.usuario import Usuario

from app.schemas.viaje_schema import ViajeCreate
from app.schemas.oferta_schema import OfertaCreate


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
# CREAR VIAJE
# ==============================

@router.post("/crear_viaje")

def crear_viaje(viaje: ViajeCreate, db: Session = Depends(get_db)):

    nuevo = Viaje(

        cliente_id=viaje.cliente_id,

        origen=viaje.origen,
        destino=viaje.destino,

        referencia_recojo=viaje.referencia_recojo,

        lat_origen=viaje.lat_origen,
        lng_origen=viaje.lng_origen,

        lat_destino=viaje.lat_destino,
        lng_destino=viaje.lng_destino,

        precio_cliente=viaje.precio_cliente,

        estado="oferta_cliente"

    )

    db.add(nuevo)

    db.commit()

    db.refresh(nuevo)

    return {
        "mensaje": "viaje creado",
        "viaje_id": nuevo.id
    }


# ==============================
# VIAJES DISPONIBLES
# ==============================

@router.get("/viajes_disponibles")

def viajes_disponibles(db: Session = Depends(get_db)):

    viajes = db.query(Viaje).filter(
        Viaje.estado == "oferta_cliente"
    ).all()

    return viajes


# ==============================
# CONDUCTOR PROPONE PRECIO
# ==============================

@router.post("/proponer_precio")

def proponer_precio(oferta: OfertaCreate, db: Session = Depends(get_db)):

    nueva_oferta = Oferta(

        viaje_id=oferta.viaje_id,

        conductor_id=oferta.conductor_id,

        precio_ofrecido=oferta.precio_ofrecido,

        estado="activa"

    )

    db.add(nueva_oferta)

    db.commit()

    db.refresh(nueva_oferta)

    return {
        "mensaje": "oferta enviada",
        "oferta_id": nueva_oferta.id
    }


# ==============================
# VER OFERTAS DE UN VIAJE
# ==============================

@router.get("/ofertas_viaje/{viaje_id}")

def ver_ofertas(viaje_id: int, db: Session = Depends(get_db)):

    ofertas = db.query(Oferta).filter(
        Oferta.viaje_id == viaje_id
    ).all()

    return ofertas


# ==============================
# CLIENTE ACEPTA OFERTA
# ==============================

@router.post("/aceptar_oferta/{oferta_id}")

def aceptar_oferta(oferta_id: int, db: Session = Depends(get_db)):

    oferta = db.query(Oferta).filter(
        Oferta.id == oferta_id
    ).first()

    if not oferta:

        raise HTTPException(
            status_code=404,
            detail="Oferta no encontrada"
        )

    viaje = db.query(Viaje).filter(
        Viaje.id == oferta.viaje_id
    ).first()

    if not viaje:

        raise HTTPException(
            status_code=404,
            detail="Viaje no encontrado"
        )

    viaje.conductor_id = oferta.conductor_id
    viaje.precio_acordado = oferta.precio_ofrecido
    viaje.estado = "conductor_asignado"

    otras_ofertas = db.query(Oferta).filter(
        Oferta.viaje_id == viaje.id
    ).all()

    for o in otras_ofertas:

        if o.id != oferta.id:
            o.estado = "rechazada"

    oferta.estado = "aceptada"

    db.commit()

    return {
        "mensaje": "oferta aceptada",
        "viaje_id": viaje.id,
        "conductor_id": viaje.conductor_id,
        "precio": viaje.precio_acordado
    }


# ==============================
# VER UBICACIÓN DEL CONDUCTOR
# ==============================

@router.get("/conductor_viaje/{viaje_id}")

def conductor_viaje(viaje_id: int, db: Session = Depends(get_db)):

    viaje = db.query(Viaje).filter(
        Viaje.id == viaje_id
    ).first()

    if not viaje:

        raise HTTPException(
            status_code=404,
            detail="Viaje no encontrado"
        )

    if not viaje.conductor_id:

        raise HTTPException(
            status_code=400,
            detail="Viaje aún sin conductor"
        )

    conductor = db.query(Usuario).filter(
        Usuario.id == viaje.conductor_id
    ).first()

    return {

        "conductor_id": conductor.id,

        "latitud": conductor.latitud,

        "longitud": conductor.longitud,

        "estado_viaje": viaje.estado

    }


# ==============================
# CONDUCTOR EN CAMINO
# ==============================

@router.post("/conductor_en_camino/{viaje_id}")

def conductor_en_camino(viaje_id: int, db: Session = Depends(get_db)):

    viaje = db.query(Viaje).filter(
        Viaje.id == viaje_id
    ).first()

    viaje.estado = "conductor_en_camino"

    db.commit()

    return {"mensaje": "conductor en camino"}


# ==============================
# CONDUCTOR LLEGÓ
# ==============================

@router.post("/conductor_llego/{viaje_id}")

def conductor_llego(viaje_id: int, db: Session = Depends(get_db)):

    viaje = db.query(Viaje).filter(
        Viaje.id == viaje_id
    ).first()

    viaje.estado = "conductor_llego"

    db.commit()

    return {"mensaje": "conductor llegó"}


# ==============================
# INICIAR VIAJE
# ==============================

@router.post("/iniciar_viaje/{viaje_id}")

def iniciar_viaje(viaje_id: int, db: Session = Depends(get_db)):

    viaje = db.query(Viaje).filter(
        Viaje.id == viaje_id
    ).first()

    viaje.estado = "viaje_en_progreso"

    db.commit()

    return {"mensaje": "viaje iniciado"}


# ==============================
# FINALIZAR VIAJE
# ==============================

@router.post("/finalizar_viaje/{viaje_id}")

def finalizar_viaje(viaje_id: int, db: Session = Depends(get_db)):

    viaje = db.query(Viaje).filter(
        Viaje.id == viaje_id
    ).first()

    viaje.estado = "finalizado"

    db.commit()

    return {"mensaje": "viaje finalizado"}