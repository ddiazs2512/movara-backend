from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from database import SessionLocal
import time
from firebase_admin import db as firebase_db
from routers.viajes import asignar_conductor_seguro
from database import get_db
from models import Viaje, Oferta, Conductor, Usuario, FCMToken, puede_transicionar
from routers.usuarios import get_current_user
from firebase_service import enviar_notificacion_data
from routers.viajes import actualizar_estado_viaje
from websocket_manager import manager


router = APIRouter()

# ======================
# SCHEMA
# ======================

class ResponderOfertaRequest(BaseModel):
    viaje_id: int
    precio: float
    accion: str
    conductor_id: int | None = None

# ======================
# OBTENER OFERTAS
# ======================

@router.get("/ofertas/{viaje_id}")
def obtener_ofertas(
    viaje_id: int,
    db: Session = Depends(get_db)
):

    ofertas = db.query(Oferta, Usuario).join(
        Usuario, Usuario.id == Oferta.conductor_id
    ).filter(
        Oferta.viaje_id == viaje_id,
        Oferta.estado == "activa"
    ).all()

    resultado = []

    for o, conductor in ofertas:
        resultado.append({
            "id": o.id,
            "viaje_id": o.viaje_id,
            "conductor_id": o.conductor_id,
            "conductor_nombre": conductor.nombre if conductor else "Desconocido",
            "precio": o.precio,
            "estado": o.estado,
            "fecha_creacion": o.fecha_creacion.isoformat() if o.fecha_creacion else None,
            "rating": conductor.rating if conductor else 0.0,
            "total_viajes": conductor.total_viajes if conductor else 0
        })

    return resultado

# ======================
# RESPONDER OFERTA
# ======================
@router.post("/responder_oferta")
async def responder_oferta(
    data: ResponderOfertaRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):

    if data.accion == "aceptar":
        viaje = db.query(Viaje).filter(
            Viaje.id == data.viaje_id
        ).with_for_update().first()
    else:
        viaje = db.query(Viaje).filter(
            Viaje.id == data.viaje_id
        ).first()

    if not viaje:
        raise HTTPException(404, "Viaje no encontrado")

    # ======================
    # OFERTAR
    # ======================
    if data.accion == "ofertar":

        if current_user.rol != "conductor":
            raise HTTPException(403, "Solo conductores pueden ofertar")

        if viaje.estado != "oferta":
            raise HTTPException(400, f"No se puede ofertar en estado {viaje.estado}")

        if data.precio <= 0:
            raise HTTPException(400, "Precio inválido")

        conductor = db.query(Conductor).filter(
            Conductor.usuario_id == current_user.id
        ).first()

        if not conductor:
            raise HTTPException(403, "No eres conductor")

        usuario = db.query(Usuario).filter(
            Usuario.id == current_user.id
        ).first()

        if not usuario or not usuario.activo:
            raise HTTPException(403, "Usuario inhabilitado")

        if viaje.conductor_id is not None:
            raise HTTPException(403, "Viaje ya asignado")

        existente = db.query(Oferta).filter(
            Oferta.viaje_id == data.viaje_id,
            Oferta.conductor_id == current_user.id,
            Oferta.estado == "activa"
        ).first()

        if existente:
            existente.precio = data.precio
            oferta = existente
        else:
            oferta = Oferta(
                viaje_id=data.viaje_id,
                conductor_id=current_user.id,
                precio=data.precio,
                estado="activa"
            )
            db.add(oferta)

        viaje.ultimo_en_ofertar = "conductor"

        db.commit()
        db.refresh(oferta)

        await manager.enviar(
            viaje.id,
            {
                "tipo": "oferta_recibida",
                "payload": {
                    "oferta_id": oferta.id,
                    "conductor_id": current_user.id,
                    "conductor_nombre": usuario.nombre,
                    "precio": oferta.precio,
                    "rating": usuario.rating or 0,
                    "total_viajes": usuario.total_viajes or 0
                }
            }
        )

        # 🔥 FIREBASE (SIN push)
        firebase_db.reference(
            f"viajes_activos/{viaje.id}/ofertas/{current_user.id}"
        ).set({
        
            "oferta_id": oferta.id,
        
            "conductor_id": current_user.id,
        
            "conductor_nombre": usuario.nombre,
        
            "precio": oferta.precio,
        
            "timestamp": int(time.time()),
        
            "rating": usuario.rating or 0,
        
            "total_viajes": usuario.total_viajes or 0
        })

        version = int(time.time() * 1000)
        
        firebase_db.reference(
            f"viajes_activos/{viaje.id}"
        ).update({
        
            "estado": "oferta",
        
            "estado_version": version,
        
            "timestamp_estado": version,
        
            "ultimo_en_ofertar": "conductor",

            "precio_conductor": oferta.precio,
        
            "metadata": {
                "ultimo_update_por": "backend"
            }
        })

        return {"mensaje": "Oferta enviada"}

    # ======================
    # RECHAZAR
    # ======================
    elif data.accion == "rechazar":

        if current_user.rol != "conductor":
            raise HTTPException(403, "Solo conductores")

        db.query(Oferta).filter(
            Oferta.viaje_id == data.viaje_id,
            Oferta.conductor_id == current_user.id,
            Oferta.estado == "activa"
        ).update({"estado": "rechazada"})

        db.commit()

        return {"mensaje": "Oferta rechazada"}

    # ======================
    # ACEPTAR
    # ======================
    elif data.accion == "aceptar":

        if current_user.rol != "cliente":
            raise HTTPException(403, "Solo clientes pueden aceptar")
    
        if viaje.cliente_id != current_user.id:
            raise HTTPException(403, "No eres el cliente")
    
        if not data.conductor_id:
            raise HTTPException(400, "Falta conductor_id")
    
        oferta = db.query(Oferta).filter(
            Oferta.viaje_id == data.viaje_id,
            Oferta.conductor_id == data.conductor_id,
            Oferta.estado == "activa"
        ).first()
    
        if not oferta:
            raise HTTPException(404, "Oferta no encontrada")
    
        # 🔒 TODO EN UNA SOLA FUNCIÓN
        viaje = asignar_conductor_seguro(
            db,
            viaje.id,
            oferta.conductor_id
        )
    
        if viaje.estado != "asignado":
            raise HTTPException(
                400,
                "estado_invalido_post_asignacion"
            )
    
        # 🔥 GUARDAR PRECIO
        viaje.precio_acordado = oferta.precio
    
        db.commit()
        db.refresh(viaje)

        await manager.enviar(
            viaje.id,
            {
                "tipo": "viaje_aceptado",
                "payload": {
                    "viaje_id": viaje.id,
                    "conductor_id": oferta.conductor_id
                }
            }
        )
    
        # =========================
        # INFO CONDUCTOR
        # =========================
    
        info_conductor = db.query(Conductor).filter(
            Conductor.usuario_id == oferta.conductor_id
        ).first()
    
        usuario_conductor = db.query(Usuario).filter(
            Usuario.id == oferta.conductor_id
        ).first()
    
        # =========================
        # FCM
        # =========================
    
        tokens = db.query(FCMToken).filter(
            FCMToken.usuario_id == oferta.conductor_id
        ).all()
    
        for t in tokens:
    
            enviar_notificacion_data(
                token=t.token,
                data={
                    "type": "conductor_asignado",
                    "viaje_id": str(viaje.id)
                }
            )
    
        # =========================
        # FIREBASE
        # =========================
    
        version = int(time.time() * 1000)
        
        firebase_db.reference(
            f"viajes_activos/{viaje.id}"
        ).update({
        
            "estado": "asignado",
        
            "estado_version": version,
            "timestamp_estado": version,
        
            "conductor_id": oferta.conductor_id,
        
            "conductor_nombre":
                usuario_conductor.nombre
                if usuario_conductor else None,
        
            "marca":
                info_conductor.marca
                if info_conductor else None,
        
            "modelo":
                info_conductor.modelo
                if info_conductor else None,
        
            "placa":
                info_conductor.placa
                if info_conductor else None,
        
            "color":
                info_conductor.color_vehiculo
                if info_conductor else None,
        
            "precio_acordado": oferta.precio,
        
            "ofertas": {},
        
            "metadata/ultimo_update_por":
                "backend"
        })
    
        return {
            "mensaje": "Conductor elegido"
        }

    # ======================
    # EN CAMINO
    # ======================
    elif data.accion == "en_camino":


        if current_user.rol != "conductor":
            raise HTTPException(403, "Solo conductores")

        if viaje.conductor_id != current_user.id:
            raise HTTPException(403, "No eres el conductor")

        actualizar_estado_viaje(db, viaje, "en_camino")

        version = int(time.time() * 1000)

        firebase_db.reference(
            f"viajes_activos/{viaje.id}"
        ).update({
            "estado": "en_camino",
            "estado_version": version,
            "timestamp_estado": version,
            "metadata": {
                "ultimo_update_por": "backend"
            }
        })

        tokens = db.query(FCMToken).join(Usuario).filter(
            FCMToken.usuario_id == viaje.cliente_id,
            Usuario.activo == True
        ).all()

        for t in tokens:
            enviar_notificacion_data(
                token=t.token,
                data={
                    "type": "conductor_en_camino",
                    "viaje_id": str(viaje.id)
                }
            )

        return {"mensaje": "Conductor en camino"}

    # ======================
    # LLEGADO
    # ======================
    elif data.accion == "llegado":

        if current_user.rol != "conductor":
            raise HTTPException(403, "Solo conductores")

        if viaje.conductor_id != current_user.id:
            raise HTTPException(403, "No eres el conductor")

        actualizar_estado_viaje(db, viaje, "llegado")

        version = int(time.time() * 1000)

        firebase_db.reference(
            f"viajes_activos/{viaje.id}"
        ).update({
            "estado": "llegado",
            "estado_version": version,
            "timestamp_estado": version,
            "metadata": {
                "ultimo_update_por": "backend"
            }
        })

        tokens = db.query(FCMToken).join(Usuario).filter(
            FCMToken.usuario_id == viaje.cliente_id,
            Usuario.activo == True
        ).all() 

        for t in tokens:
            enviar_notificacion_data(
                token=t.token,
                data={
                    "type": "conductor_llego",
                    "viaje_id": str(viaje.id),
                    "title": "🚗 Tu conductor llegó",
                    "body": "El conductor ya está en el punto de recojo"
                }
            )

        return {"mensaje": "Conductor llegó"}

    # ======================
    # INICIAR
    # ======================
    elif data.accion == "iniciar":

        if current_user.rol != "conductor":
            raise HTTPException(403, "Solo conductores")

        if viaje.conductor_id != current_user.id:
            raise HTTPException(403, "No eres el conductor")

        actualizar_estado_viaje(db, viaje, "en_curso")

        version = int(time.time() * 1000)

        firebase_db.reference(
            f"viajes_activos/{viaje.id}"
        ).update({
            "estado": "en_curso",
            "estado_version": version,
            "timestamp_estado": version,
            "metadata": {
                "ultimo_update_por": "backend"
            }
        })
        
        viaje.fecha_inicio = datetime.utcnow()
        db.commit()

        tokens = db.query(FCMToken).join(Usuario).filter(
            FCMToken.usuario_id == viaje.cliente_id,
            Usuario.activo == True
        ).all()

        for t in tokens:
            enviar_notificacion_data(
                token=t.token,
                data={
                    "type": "viaje_iniciado",
                    "viaje_id": str(viaje.id)
                }
            )

        return {"mensaje": "Viaje iniciado"}
    
    # ======================
    # EN_CURSO
    # ======================

    elif data.accion == "en_curso":

        if current_user.rol != "conductor":
            raise HTTPException(403, "Solo conductores")
    
        if viaje.conductor_id != current_user.id:
            raise HTTPException(403, "No eres el conductor")
    
        actualizar_estado_viaje(db, viaje, "en_curso")
    
        viaje.fecha_inicio = datetime.utcnow()
        db.commit()
    
        version = int(time.time() * 1000)
    
        firebase_db.reference(
            f"viajes_activos/{viaje.id}"
        ).update({
            "estado": "en_curso",
            "estado_version": version,
            "timestamp_estado": version,
            "metadata": {
                "ultimo_update_por": "backend"
            }
        })
    
        tokens = db.query(FCMToken).filter(
            FCMToken.usuario_id == viaje.cliente_id
        ).all()
    
        for t in tokens:
            enviar_notificacion_data(
                token=t.token,
                data={
                    "type": "viaje_iniciado",
                    "viaje_id": str(viaje.id)
                }
            )
    
        return {
            "mensaje": "Viaje iniciado"
        }
    # ======================
    # FINALIZAR
    # ======================
    elif data.accion == "finalizar":

        if current_user.rol != "conductor":
            raise HTTPException(403, "Solo conductores")

        if viaje.estado == "finalizado":
            return {"mensaje": "Ya estaba finalizado"}

        if viaje.conductor_id != current_user.id:
            raise HTTPException(403, "No eres el conductor")

        actualizar_estado_viaje(db, viaje, "finalizado")
        viaje.fecha_fin = datetime.utcnow()
        db.commit()
        db.refresh(viaje)

        # 🔥 ACTUALIZAR FIREBASE
        version = int(time.time() * 1000)

        firebase_db.reference(
            f"viajes_activos/{viaje.id}"
        ).update({
            "estado": "finalizado",
            "estado_version": version,
            "timestamp_estado": version,
            "metadata/ultimo_update_por": "backend"
        })

        # 🔥 ELIMINAR NODO (CLAVE)
        firebase_db.reference(f"viajes_activos/{viaje.id}").delete()

        # 🔥 ACTUALIZAR MÉTRICAS
        conductor_user = db.query(Usuario).filter(
            Usuario.id == viaje.conductor_id
        ).first()

        if conductor_user:
            conductor_user.total_viajes = (conductor_user.total_viajes or 0) + 1
            db.commit()
        
        tokens = db.query(FCMToken).join(Usuario).filter(
            FCMToken.usuario_id == viaje.cliente_id,
            Usuario.activo == True
        ).all()

        for t in tokens:
            enviar_notificacion_data(
                token=t.token,
                data={
                    "type": "viaje_finalizado",
                    "viaje_id": str(viaje.id)
                }
            )

        return {"mensaje": "Viaje finalizado"}
