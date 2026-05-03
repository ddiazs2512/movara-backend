from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from routers.usuarios import get_current_user

from database import get_db
from models import Viaje, Evaluacion, Usuario

router = APIRouter()

# ======================
# SCHEMA
# ======================

class EvaluacionRequest(BaseModel):
    viaje_id: int
    evaluado_id: int
    rol_evaluado: str
    estrellas: int
    comentario: str = ""

# ======================
# EVALUAR
# ======================

@router.post("/evaluar")
def evaluar(
    data: EvaluacionRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    viaje = db.query(Viaje).filter(Viaje.id == data.viaje_id).first()

    if not viaje:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")

    # 🔴 Validar que terminó el viaje
    if not viaje.fecha_fin:
        raise HTTPException(
            status_code=400,
            detail=f"Viaje no listo para evaluar. Estado: {viaje.estado}"
        )

    # 🔒 Validar estrellas
    if data.estrellas < 1 or data.estrellas > 5:
        raise HTTPException(status_code=400, detail="Estrellas debe ser entre 1 y 5")

    evaluador_id = current_user.id

    # 🔒 Validar participación
    participantes = [viaje.cliente_id]
    if viaje.conductor_id:
        participantes.append(viaje.conductor_id)

    if evaluador_id not in participantes:
        raise HTTPException(status_code=403, detail="No participaste en este viaje")

    # 🎯 Determinar evaluado REAL
    if evaluador_id == viaje.cliente_id:
        if not viaje.conductor_id:
            raise HTTPException(400, "Viaje sin conductor asignado")
        evaluado_id = viaje.conductor_id
        rol_real = "conductor"

    elif evaluador_id == viaje.conductor_id:
        evaluado_id = viaje.cliente_id
        rol_real = "cliente"

    else:
        raise HTTPException(403, "No participaste en este viaje")

    # 🔒 Evitar autoevaluación
    if evaluador_id == evaluado_id:
        raise HTTPException(status_code=400, detail="No puedes evaluarte a ti mismo")

    # 🔥 EVITAR DUPLICADO
    existente = db.query(Evaluacion).filter(
        Evaluacion.viaje_id == data.viaje_id,
        Evaluacion.evaluador_id == evaluador_id
    ).first()

    if existente:
        return {
            "ok": True,
            "data": {
                "mensaje": "Ya evaluado",
                "evaluacion_id": existente.id
            }
        }

    # 💾 Crear evaluación
    nueva = Evaluacion(
        viaje_id=data.viaje_id,
        evaluador_id=evaluador_id,
        evaluado_id=evaluado_id,
        rol_evaluado=rol_real,
        estrellas=data.estrellas,
        comentario=data.comentario or ""
    )

    db.add(nueva)
    db.commit()
    db.refresh(nueva)

    # 🔥 RECALCULAR RATING
    evaluaciones = db.query(Evaluacion).filter(
        Evaluacion.evaluado_id == evaluado_id,
        Evaluacion.rol_evaluado == rol_real
    ).all()

    if evaluaciones:
        promedio = sum(e.estrellas for e in evaluaciones) / len(evaluaciones)

        usuario_eval = db.query(Usuario).filter(
            Usuario.id == evaluado_id
        ).first()

        if usuario_eval:
            usuario_eval.rating = round(promedio, 2)
            db.commit()

    # 🔥 marcar viaje evaluado si ambos evaluaron
    evaluadores = db.query(Evaluacion.evaluador_id).filter(
        Evaluacion.viaje_id == data.viaje_id
    ).all()

    ids = {e[0] for e in evaluadores}

    return {
        "ok": True,
        "data": {
            "mensaje": "Evaluación guardada",
            "evaluacion_id": nueva.id
        }
    }

# ======================
# OBTENER EVALUACIONES
# ======================

@router.get("/evaluaciones/{usuario_id}")
def obtener_evaluaciones(
    usuario_id: int,
    db: Session = Depends(get_db)
):
    # 🔍 buscar usuario
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # 🔍 buscar evaluaciones reales
    evaluaciones = db.query(Evaluacion).filter(
        Evaluacion.evaluado_id == usuario_id
    ).order_by(Evaluacion.id.desc()).all()

    total = len(evaluaciones)

    # 🎯 CASO 1: tiene evaluaciones reales
    if total > 0:
        promedio = sum(e.estrellas for e in evaluaciones) / total

        return {
            "ok": True,
            "data": {
                "promedio": round(promedio, 1),
                "total": total,
                "evaluaciones": [
                    {
                        "estrellas": e.estrellas,
                        "comentario": e.comentario,
                        "fecha": e.fecha.isoformat() if e.fecha else None
                    }
                    for e in evaluaciones
                ]
            }
        }

    # 🎯 CASO 2: NO tiene evaluaciones → fallback a usuario.rating
    return {
        "ok": True,
        "data": {
            "promedio": usuario.rating if usuario.rating else 0,
            "total": 0,
            "evaluaciones": []
        }
    }