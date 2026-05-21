from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import random  # 🔥 IMPORT NECESARIO
from models import Viaje, Usuario, Conductor, Oferta, Evaluacion, Mensaje, FCMToken, Ubicacion
from database import get_db
from firebase_service import enviar_notificacion_data
import math
from schemas import ResponderOfertaRequest, ViajeResponse
from firebase_admin import db as firebase_db
import time
import requests
from models import puede_transicionar
from routers.usuarios import get_current_user
from schemas import ViajeActivoResponse
from fastapi import Request

def actualizar_estado_viaje(db, viaje, nuevo_estado):
    if not puede_transicionar(viaje.estado, nuevo_estado):
        raise HTTPException(400, f"No se puede pasar de {viaje.estado} a {nuevo_estado}")

    viaje.estado = nuevo_estado
    viaje.fecha_ultima_accion = datetime.utcnow()

    db.commit()
    db.refresh(viaje)

    ref = firebase_db.reference(f"viajes_activos/{viaje.id}")

    data = {
        "estado": nuevo_estado,
        "timestamp_estado": int(time.time() * 1000),
        "metadata": {
            "ultimo_update_por": "backend"
        }
    }

    try:
        ref.update(data)
    except Exception as e:
        print("❌ FIREBASE FALLÓ - ESTADO DESINCRONIZADO:", e)

    return viaje

def calcular_distancia_metros(lat1, lon1, lat2, lon2):
    R = 6371000  # radio tierra en metros

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c

router = APIRouter()

# ======================
# 🔒 ASIGNAR CONDUCTOR (SEGURO)
# ======================
def asignar_conductor_seguro(db: Session, viaje_id: int, conductor_id: int):

    # 🔒 BLOQUEO
    viaje = db.query(Viaje)\
        .filter(Viaje.id == viaje_id)\
        .with_for_update()\
        .first()

    if not viaje:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")

    if not puede_transicionar(viaje.estado, "asignado"):
        raise HTTPException(status_code=400, detail=f"No se puede aceptar en estado {viaje.estado}")

    if viaje.conductor_id is not None:
        raise HTTPException(status_code=409, detail="Viaje ya fue tomado")

    conductor = db.query(Usuario).filter(
        Usuario.id == conductor_id,
        Usuario.rol == "conductor",
        Usuario.activo == True
    ).first()

    if not conductor:
        raise HTTPException(status_code=403, detail="Conductor inválido")

    # =========================
    # ✅ CAMBIO DE ESTADO (BD)
    # =========================
    viaje.conductor_id = conductor_id
    actualizar_estado_viaje(db, viaje, "asignado")
    db.refresh(viaje)

    # =========================
    # 🔥 FIREBASE (DESPUÉS)
    # =========================
    try:
        firebase_db.reference(f"viajes_activos/{viaje.id}").update({
            "ofertas": None,          # 🔥 mejor que {}
            "conductor_id": conductor_id
        })
    except Exception as e:
        # ⚠️ LOG, pero NO romper flujo
        print(f"ERROR FIREBASE: {e}")

    return viaje

def obtener_ruta_google(lat1, lng1, lat2, lng2):
    import os
    API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

    if not API_KEY:
        raise Exception("GOOGLE_MAPS_API_KEY no configurada")

    url = "https://maps.googleapis.com/maps/api/directions/json"

    params = {
        "origin": f"{lat1},{lng1}",
        "destination": f"{lat2},{lng2}",
        "key": API_KEY,
        "mode": "driving"
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data["status"] != "OK":
        return None

    route = data["routes"][0]
    leg = route["legs"][0]

    return {
        "distancia_texto": leg["distance"]["text"],
        "distancia_metros": leg["distance"]["value"],
        "duracion_texto": leg["duration"]["text"],
        "duracion_segundos": leg["duration"]["value"],
        "polyline": route["overview_polyline"]["points"]
    }

# ======================
# SCHEMAS
# ======================

class ViajeCreate(BaseModel):
    origen: str
    destino: str
    precio_propuesto: float
    lat_origen: float
    lng_origen: float
    lat_destino: float
    lng_destino: float
    ciudad: str

class UbicacionRequest(BaseModel):
    viaje_id: int
    lat: float
    lng: float

class EvaluacionRequest(BaseModel):
    viaje_id: int
    evaluador_id: int
    evaluado_id: int
    rol_evaluado: str
    estrellas: int
    comentario: str = ""

class CancelarViajeRequest(BaseModel):
    viaje_id: int
    motivo: str = "Cancelado"

class MensajeRequest(BaseModel):
    viaje_id: int
    emisor_id: int
    receptor_id: int
    mensaje: str

class CambiarEstadoRequest(BaseModel):
    viaje_id: int
    estado: str

class UbicacionConductorRequest(BaseModel):
    lat: float
    lng: float

# ======================
# ALMACENAMIENTO TEMPORAL
# ======================

ubicaciones_temp = {}  # viaje_id -> {lat, lng, timestamp}

# ======================
# CREAR VIAJE + NOTIFICAR
# ======================

def calcular_score(usuario, conductor_info):
    score = 0

    # ⭐ Reputación
    rating = getattr(usuario, "rating", 5) or 5
    score += rating * 0.4

    # 🚗 Experiencia
    viajes = getattr(usuario, "viajes_completados", 0) or 0
    score += viajes * 0.01

    # 🟢 Actividad reciente
    ultimo_login = getattr(usuario, "ultimo_login", None)
    if ultimo_login:
        minutos = (datetime.utcnow() - ultimo_login).total_seconds() / 60
        if minutos < 10:
            score += 1
        elif minutos < 60:
            score += 0.5

    # 🆕 Boost nuevos
    if viajes < 20:
        score += 1.5

    # 🔄 Penalización si acaba de ganar
    ultimo_viaje = getattr(usuario, "ultimo_viaje_asignado", None)
    if ultimo_viaje:
        minutos = (datetime.utcnow() - ultimo_viaje).total_seconds() / 60
        if minutos < 5:
            score -= 2
        elif minutos < 15:
            score -= 1

    # 🛵 Vehículo
    if conductor_info and getattr(conductor_info, "anio", None):
        if conductor_info.anio >= 2022:
            score += 0.3
        elif conductor_info.anio >= 2018:
            score += 0.1

    return score

@router.post("/crear_viaje")
def crear_viaje(
    viaje: ViajeCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    cliente_id = current_user.id

    ciudad = viaje.ciudad.strip().lower()

    # ======================
    # VALIDAR VIAJE ACTIVO
    # ======================
    activos = db.query(Viaje.id).filter(
        Viaje.cliente_id == cliente_id,
        Viaje.estado.in_(["oferta","asignado","en_camino","llegado","en_curso"])
    ).all()

    if len(activos) > 0:
        raise HTTPException(400, "Ya tienes un viaje activo")
        

    # ======================
    # CREAR VIAJE
    # ======================
    nuevo = Viaje(
        cliente_id=cliente_id,
        referencia_recojo=viaje.origen,
        destino_referencia=viaje.destino,
        lat_origen=viaje.lat_origen,
        lng_origen=viaje.lng_origen,
        lat_destino=viaje.lat_destino,
        lng_destino=viaje.lng_destino,
        precio_cliente_1=viaje.precio_propuesto,
        estado="oferta",
        ultimo_en_ofertar="cliente",
        ciudad=ciudad
    )

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    # ======================
    # FIREBASE
    # ======================
    from firebase_admin import db as firebase_db

    ruta = obtener_ruta_google(
        nuevo.lat_origen,
        nuevo.lng_origen,
        nuevo.lat_destino,
        nuevo.lng_destino
    )

    cliente = db.query(Usuario).filter(Usuario.id == nuevo.cliente_id).first()

    firebase_db.reference(f"viajes_activos/{nuevo.id}").set({
        "estado": "oferta",
        "cliente_id": nuevo.cliente_id,
        "cliente_nombre": cliente.nombre if cliente else "Cliente",
        "conductor_id": None,
        "precio_acordado": None,
        "precio_cliente": nuevo.precio_cliente_1,
        "ubicacion_conductor": None,
        "timestamp_estado": int(time.time() * 1000),
        "ofertas": {},
        "lat_origen": nuevo.lat_origen,
        "lng_origen": nuevo.lng_origen,
        "lat_destino": nuevo.lat_destino,
        "lng_destino": nuevo.lng_destino,
        "ruta": ruta if ruta else None,
        "metadata": {
            "origen": nuevo.referencia_recojo,
            "destino": nuevo.destino_referencia,
            "ultimo_update_por": "backend"
        }
    })

    # ======================
    # CONDUCTORES DISPONIBLES
    # ======================
    from datetime import timedelta

    limite = datetime.utcnow() - timedelta(seconds=20)

    conductores = db.query(Usuario).join(
        Ubicacion,
        Ubicacion.conductor_id == Usuario.id
    ).filter(
        Usuario.rol == "conductor",
        Usuario.modo_actual == "conductor",
        Usuario.activo == True,
        Ubicacion.viaje_id == None,
        Ubicacion.updated_at >= limite
    ).distinct(Usuario.id).all()

    if not conductores:
        print(f"⚠️ No hay conductores en ciudad: {ciudad}")
        conductores = []

    # ======================
    # FILTRO POR DISTANCIA
    # ======================
    candidatos = []

    for c in conductores:

        ubicacion = db.query(Ubicacion).filter(
            Ubicacion.conductor_id == c.id,
            Ubicacion.viaje_id == None
        ).order_by(Ubicacion.updated_at.desc()).first()

        if not ubicacion:
            continue

        distancia = calcular_distancia_metros(
            nuevo.lat_origen,
            nuevo.lng_origen,
            ubicacion.lat,
            ubicacion.lng
        )
        print(
            "CONDUCTOR",
            c.id,
            c.nombre,
            "DISTANCIA:",
            distancia
        )

        print("==============")
        print("CLIENTE:", data.lat_origen, data.lng_origen)
        print("CONDUCTOR:", ubicacion.lat, ubicacion.lng)
        print("DISTANCIA:", distancia)
        print("==============")

        if distancia <= 4000:
            candidatos.append(c)

    if not candidatos:
        print("⚠️ No hay conductores cercanos, no se envía notificación")
        candidatos = []

    # ======================
    # NOTIFICACIONES
    # ======================
    for usuario in candidatos:

        tokens = db.query(FCMToken).join(Usuario).filter(
            FCMToken.usuario_id == usuario.id,
            Usuario.activo == True
        ).all()

        for t in tokens:
            enviar_notificacion_data(
                token=t.token,
                data={
                    "type": "nuevo_viaje",
                    "viaje_id": str(nuevo.id)
                }
            )

    # ======================
    # RESPUESTA
    # ======================
    return {
        "mensaje": "Viaje creado",
        "viaje_id": nuevo.id
    }

@router.get("/viaje/{viaje_id}", response_model=ViajeResponse)
def get_viaje(
    viaje_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):

    viaje = db.query(Viaje).filter(Viaje.id == viaje_id).first()

    if not viaje:
        raise HTTPException(404, "Viaje no encontrado")

    # 🔒 seguridad
    if viaje.cliente_id != current_user.id and viaje.conductor_id != current_user.id:
        raise HTTPException(403, "No autorizado")

    # 👤 usuarios
    conductor_usuario = db.query(Usuario).filter(
        Usuario.id == viaje.conductor_id
    ).first()

    cliente_usuario = db.query(Usuario).filter(
        Usuario.id == viaje.cliente_id
    ).first()

    # 🚗 datos vehículo
    conductor = db.query(Conductor).filter(
        Conductor.usuario_id == viaje.conductor_id
    ).first()

    # 📍 ubicación REAL (tabla Ubicacion)
    from datetime import timedelta

    limite = datetime.utcnow() - timedelta(seconds=20)

    ubicacion = db.query(Ubicacion).filter(
        Ubicacion.viaje_id == viaje.id,
        Ubicacion.updated_at >= limite
    ).order_by(
        Ubicacion.updated_at.desc()
    ).first()

    return {
        "id": viaje.id,
        "estado": viaje.estado,

        "lat_origen": viaje.lat_origen,
        "lng_origen": viaje.lng_origen,
        "lat_destino": viaje.lat_destino,
        "lng_destino": viaje.lng_destino,

        # 📍 CORRECTO
        "lat_conductor": ubicacion.lat if ubicacion else None,
        "lng_conductor": ubicacion.lng if ubicacion else None,

        "referencia_recojo": viaje.referencia_recojo,
        "destino_referencia": viaje.destino_referencia,
        "precio_acordado": viaje.precio_acordado,

        # 🚗 CONDUCTOR
        "conductor_id": viaje.conductor_id,
        "conductor_nombre": conductor_usuario.nombre if conductor_usuario else None,
        "conductor_telefono": conductor_usuario.telefono if conductor_usuario else None,

        # 👤 CLIENTE
        "cliente_id": viaje.cliente_id,
        "cliente_nombre": cliente_usuario.nombre if cliente_usuario else None,
        "cliente_telefono": cliente_usuario.telefono if cliente_usuario else None,

        # 🚘 VEHÍCULO
        "marca": conductor.marca if conductor else None,
        "modelo": conductor.modelo if conductor else None,
        "color_vehiculo": conductor.color_vehiculo if conductor else None,
        "placa": conductor.placa if conductor else None,
    }

# ======================
# MIS VIAJES (CLIENTE) - ENRIQUECIDO
# ======================

@router.get("/mis_viajes")
def mis_viajes(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    viajes = db.query(Viaje).filter(
        Viaje.cliente_id == current_user.id,
        Viaje.estado.notin_(["finalizado", "cancelado"])
    ).order_by(Viaje.id.desc()).all()

    resultado = []
    for v in viajes:
        data = {
            "id": v.id,
            "referencia_recojo": v.referencia_recojo,
            "destino_referencia": v.destino_referencia,
            "precio_cliente": v.precio_cliente_1,
            "precio_conductor": v.precio_conductor,
            "precio_acordado": v.precio_acordado,
            "estado": v.estado,
            "conductor_id": v.conductor_id,
            "cliente_id": v.cliente_id,
            "lat_origen": v.lat_origen,
            "lng_origen": v.lng_origen,
            "lat_destino": v.lat_destino,
            "lng_destino": v.lng_destino,
            "ultimo_en_ofertar": v.ultimo_en_ofertar,
            "cliente_nombre": None,
            "cliente_telefono": None,
            "conductor_nombre": None,
            "conductor_telefono": None,
            "placa": None,
            "color_vehiculo": None,
            "marca": None,
            "modelo": None
        }

        # Datos cliente
        cliente = db.query(Usuario).filter(Usuario.id == v.cliente_id).first()
        if cliente:
            data["cliente_nombre"] = cliente.nombre
            data["cliente_telefono"] = cliente.telefono

        # Datos conductor según estado
        if v.conductor_id:
            conductor_user = db.query(Usuario).filter(Usuario.id == v.conductor_id).first()
            conductor_info = db.query(Conductor).filter(Conductor.usuario_id == v.conductor_id).first()

            if v.estado in ["asignado", "en_camino", "llegado", "en_curso"]:
                if conductor_user:
                    data["conductor_nombre"] = conductor_user.nombre
                if conductor_info:
                    data["placa"] = conductor_info.placa
                    data["color_vehiculo"] = conductor_info.color_vehiculo
                    data["marca"] = conductor_info.marca
                    data["modelo"] = conductor_info.modelo

            elif v.estado in ["finalizado", "evaluado"]:
                if conductor_user:
                    data["conductor_nombre"] = conductor_user.nombre

        resultado.append(data)

    return resultado

@router.get("/viajes-disponibles")
def viajes_disponibles(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):

    viajes = db.query(Viaje).filter(
        Viaje.estado == "oferta"
    ).all()

    resultado = []

    # 🔥 UBICACIÓN DEL CONDUCTOR
    from datetime import timedelta

    limite = datetime.utcnow() - timedelta(seconds=20)

    ubicacion_conductor = db.query(Ubicacion).filter(
        Ubicacion.conductor_id == current_user.id,
        Ubicacion.viaje_id == None,
        Ubicacion.updated_at >= limite
    ).order_by(
        Ubicacion.updated_at.desc()
    ).first()

    # 🔴 SIN UBICACIÓN → NO MOSTRAR NADA
    if not ubicacion_conductor:
        return []

    # 🔥 RADIO MÁXIMO
    MAX_DIST = 4000  # metros

    for v in viajes:

        # ======================
        # 📏 DISTANCIA
        # ======================
        distancia = calcular_distancia_metros(
            ubicacion_conductor.lat,
            ubicacion_conductor.lng,
            v.lat_origen,
            v.lng_origen
        )

        # 🔥 FILTRO REAL (CLAVE)
        if distancia > MAX_DIST:
            continue

        # ======================
        # 🗺️ RUTA (OPCIONAL)
        # ======================
        ruta = obtener_ruta_google(
            v.lat_origen,
            v.lng_origen,
            v.lat_destino,
            v.lng_destino
        )

        resultado.append({
            "id": v.id,
            "referencia_recojo": v.referencia_recojo,
            "destino_referencia": v.destino_referencia,
            "precio_cliente": v.precio_cliente_1,
            "precio_conductor": None,
            "precio_acordado": None,
            "estado": v.estado,
            "conductor_id": None,
            "cliente_id": v.cliente_id,
            "lat_origen": v.lat_origen,
            "lng_origen": v.lng_origen,
            "lat_destino": v.lat_destino,
            "lng_destino": v.lng_destino,
            "ultimo_en_ofertar": None,

            # 🔥 AHORA SÍ REAL
            "distancia_conductor_m": distancia,

            "ruta": {
                "distancia_texto": ruta["distancia_texto"] if ruta else None,
                "duracion_texto": ruta["duracion_texto"] if ruta else None,
                "polyline": ruta["polyline"] if ruta else None
            } if ruta else None,

            "cliente_nombre": v.cliente.nombre if v.cliente else None
        })

    return resultado

@router.get("/viaje_activo", response_model=ViajeActivoResponse)
def viaje_activo(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    # 🔥 BUSCAR VIAJE ACTIVO (CLIENTE O CONDUCTOR)
    viaje = db.query(Viaje).filter(
        (
            (Viaje.cliente_id == current_user.id) |
            (Viaje.conductor_id == current_user.id)
        ),
        Viaje.estado.in_([
            "oferta",
            "asignado",
            "en_camino",
            "llegado",
            "en_curso"
        ])
    ).order_by(Viaje.id.desc()).first()

    from datetime import timedelta

    # ======================
    # ⏰ AUTO CANCELAR VIAJES VIEJOS
    # ======================

    if viaje and viaje.estado == "oferta":

        tiempo_pasado = datetime.utcnow() - viaje.fecha_creacion

        if tiempo_pasado > timedelta(minutes=15):

            print(f"⏰ VIAJE EXPIRADO {viaje.id}")

            actualizar_estado_viaje(
                db,
                viaje,
                "cancelado"
            )

            try:
                firebase_db.reference(
                    f"viajes_activos/{viaje.id}"
                ).delete()

            except Exception as e:
                print("❌ ERROR ELIMINANDO FIREBASE:", e)

            viaje = None

    # ❌ NO HAY VIAJE ACTIVO
    if not viaje:
        return ViajeActivoResponse(
            activo=False,
            id=None,
            estado=None,
            lat_origen=None,
            lng_origen=None,
            lat_destino=None,
            lng_destino=None,
            destino_referencia=None,
            cliente_id=None,
            cliente_nombre=None,
            conductor_id=None,
            conductor_nombre=None,
            precio_acordado=None,
            marca=None,
            modelo=None,
            color_vehiculo=None,
            placa=None
        )

    # 👤 CLIENTE
    cliente = viaje.cliente
    conductor_usuario = viaje.conductor

    conductor = None
    if viaje.conductor_id:
        conductor = db.query(Conductor).filter(
            Conductor.usuario_id == viaje.conductor_id
        ).first()

    # ✅ RESPUESTA CORRECTA
    return ViajeActivoResponse(
        activo=True,
        id=viaje.id,

        # 🔥 CLAVE: ahora sí devolvemos estado
        estado=viaje.estado,

        lat_origen=viaje.lat_origen,
        lng_origen=viaje.lng_origen,
        lat_destino=viaje.lat_destino,
        lng_destino=viaje.lng_destino,
        destino_referencia=viaje.destino_referencia,

        cliente_id=viaje.cliente_id,
        cliente_nombre=cliente.nombre if cliente else None,

        conductor_id=viaje.conductor_id,
        conductor_nombre=conductor_usuario.nombre if conductor_usuario else None,

        precio_acordado=viaje.precio_acordado,

        marca=conductor.marca if conductor else None,
        modelo=conductor.modelo if conductor else None,
        color_vehiculo=conductor.color_vehiculo if conductor else None,
        placa=conductor.placa if conductor else None
    )

# ======================
# VIAJES DISPONIBLES (CONDUCTOR)
# ======================

@router.get("/viajes_pendientes")
def viajes_pendientes(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # ======================
    # 🔍 VALIDAR USUARIO
    # ======================
    usuario = db.query(Usuario).filter(
        Usuario.id == current_user.id
    ).first()

    if not usuario:
        raise HTTPException(404, "Usuario no encontrado")

    # ======================
    # 🔴 BLOQUEO SI NO ESTÁ ACTIVO
    # ======================
    if usuario.rol == "conductor" and not usuario.activo:
        return []

    # ======================
    # 📦 TRAER VIAJES DISPONIBLES
    # ======================
    viajes = db.query(Viaje).filter(
        Viaje.estado == "oferta",
        Viaje.conductor_id == None
    ).order_by(Viaje.id.desc()).all()

    resultado = []

    from datetime import timedelta
    limite = datetime.utcnow() - timedelta(seconds=20)

    # 🔥 UBICACIÓN DEL CONDUCTOR
    ubicacion_conductor = db.query(Ubicacion).filter(
        Ubicacion.conductor_id == current_user.id,
        Ubicacion.viaje_id == None,
        Ubicacion.updated_at >= limite
    ).order_by(
        Ubicacion.updated_at.desc()
    ).first()

    # 🔴 SIN UBICACIÓN → NO MOSTRAR NADA
    if not ubicacion_conductor:
        return []

    # 🔥 RADIO MÁXIMO
    MAX_DIST = 4000  # metros

    for v in viajes:

        cliente = db.query(Usuario).filter(
            Usuario.id == v.cliente_id
        ).first()

        # ======================
        # 📏 CALCULAR DISTANCIA
        # ======================
        distancia_conductor = calcular_distancia_metros(
            ubicacion_conductor.lat,
            ubicacion_conductor.lng,
            v.lat_origen,
            v.lng_origen
        )

        # 🔥 FILTRO REAL (CLAVE)
        if distancia_conductor > MAX_DIST:
            continue

        # ======================
        # 🔥 FIREBASE DATA
        # ======================
        ref = firebase_db.reference(f"viajes_activos/{v.id}")
        try:
            data_fb = ref.get() or {}
        except:
            data_fb = {}

        # ======================
        # 📦 RESPUESTA
        # ======================
        resultado.append({
            "id": v.id,
            "estado": v.estado,

            "referencia_recojo": v.referencia_recojo,
            "destino_referencia": v.destino_referencia,

            "lat_origen": v.lat_origen,
            "lng_origen": v.lng_origen,
            "lat_destino": v.lat_destino,
            "lng_destino": v.lng_destino,

            "precio_cliente": v.precio_cliente_1,
            "cliente_nombre": cliente.nombre if cliente else "Cliente",

            "distancia_conductor_m": distancia_conductor,

            "ruta": data_fb.get("ruta") if data_fb else None
        })

    return resultado

# ======================
# MIS VIAJES (CONDUCTOR) - ENRIQUECIDO
# ======================

@router.get("/mis_viajes_conductor")
def mis_viajes_conductor(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    ESTADOS_VISIBLES = [
        "asignado",
        "en_camino",
        "llegado",
        "en_curso"
    ]

    todos = db.query(Viaje).filter(
        Viaje.conductor_id == current_user.id,
        Viaje.estado.in_(ESTADOS_VISIBLES)
    ).order_by(Viaje.fecha_creacion.desc()).all()

    resultado = []

    for v in todos:
        data = {
            "id": v.id,
            "referencia_recojo": v.referencia_recojo,
            "destino_referencia": v.destino_referencia,
            "precio_cliente": v.precio_cliente_1,
            "precio_acordado": v.precio_acordado,
            "estado": v.estado,
            "lat_origen": v.lat_origen,
            "lng_origen": v.lng_origen,
            "lat_destino": v.lat_destino,
            "lng_destino": v.lng_destino,
            "cliente_id": v.cliente_id,
            "cliente_nombre": None,
            "cliente_telefono": None,
            "conductor_id": current_user.id,
            "mi_nombre": None,
            "mi_telefono": None
        }

        # 🔥 Cliente SIEMPRE que exista
        if v.cliente_id:
            cliente = db.query(Usuario).filter(Usuario.id == v.cliente_id).first()

            if cliente:
                data["cliente_nombre"] = cliente.nombre

                # Solo mostrar teléfono en estados avanzados
                if v.estado in ["en_curso", "finalizado"]:
                    data["cliente_telefono"] = cliente.telefono

                # Mis datos (conductor)
                yo = db.query(Usuario).filter(Usuario.id == current_user.id).first()
                if yo:
                    data["mi_nombre"] = yo.nombre
                    data["mi_telefono"] = yo.telefono

        resultado.append(data)

    return resultado

# ======================
# TRACKING - UBICACIÓN
# ======================

@router.post("/actualizar_ubicacion")
def actualizar_ubicacion(
    data: UbicacionRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):

    # ======================
    # LOG INICIAL
    # ======================
    
    print(f"[TRACK] REQUEST viaje={data.viaje_id} user={current_user.id}")

    viaje = db.query(Viaje).filter(Viaje.id == data.viaje_id).first()

    print(f"[TRACK] estado={viaje.estado} conductor={viaje.conductor_id}")

    # ======================
    # VALIDACIONES ESTRICTAS
    # ======================

    if not viaje:
        raise HTTPException(404, "viaje_no_existe")

    if viaje.conductor_id is None:
        raise HTTPException(409, "viaje_sin_conductor")

    if viaje.estado == "finalizado":
        raise HTTPException(409, "viaje_finalizado")

    if viaje.conductor_id != current_user.id:
        raise HTTPException(
            403,
            f"no_autorizado user={current_user.id} conductor={viaje.conductor_id}"
        )

    if viaje.estado not in ["asignado", "en_camino", "llegado", "en_curso"]:
        raise HTTPException(409, f"estado_invalido:{viaje.estado}")

    print(f"[TRACK] VALID_OK viaje={viaje.id} estado={viaje.estado}")

    # ======================
    # UPSERT UBICACION
    # ======================

    ubicacion = db.query(Ubicacion).filter(
        Ubicacion.viaje_id == data.viaje_id
    ).order_by(
        Ubicacion.updated_at.desc()
    ).first()

    if ubicacion:

        ubicacion.lat = data.lat
        ubicacion.lng = data.lng
        ubicacion.updated_at = datetime.utcnow()

    else:

        nueva = Ubicacion(
            viaje_id=data.viaje_id,
            conductor_id=current_user.id,
            lat=data.lat,
            lng=data.lng,
            updated_at=datetime.utcnow()
        )

        db.add(nueva)

    # ======================
    # ACTUALIZAR VIAJE
    # ======================

    viaje.lat_conductor = data.lat
    viaje.lng_conductor = data.lng

    try:
        db.commit()
        print(f"[TRACK] DB_OK viaje={viaje.id}")
    except Exception as e:
        print(f"[TRACK] DB_ERROR viaje={data.viaje_id} error={str(e)}")
        raise HTTPException(500, f"db_error:{str(e)}")

    # ======================
    # FIREBASE
    # ======================

    try:
        firebase_db.reference(f"viajes_activos/{viaje.id}").update({
            "ubicacion_conductor": {
                "lat": data.lat,
                "lng": data.lng
            },
            "timestamp_estado": int(time.time() * 1000),
            "metadata/ultimo_update_por": "backend"
        })
        print(f"[TRACK] FB_OK viaje={viaje.id}")

    except Exception as e:
        print(f"[TRACK] FB_ERROR viaje={viaje.id} error={str(e)}")
        raise HTTPException(500, f"firebase_error:{str(e)}")

    # ======================
    # RESPUESTA
    # ======================

    return {
        "ok": True,
        "mensaje": "Ubicación actualizada",
        "viaje_id": viaje.id,
        "lat": data.lat,
        "lng": data.lng
    }

@router.get("/ubicacion/{viaje_id}")
def obtener_ubicacion(
    viaje_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):

    from datetime import timedelta

    limite = datetime.utcnow() - timedelta(seconds=20)

    ubicacion = db.query(Ubicacion).filter(
        Ubicacion.viaje_id == viaje_id,
        Ubicacion.updated_at >= limite
    ).order_by(
        Ubicacion.updated_at.desc()
    ).first()

    if not ubicacion:
        return {"lat": 0, "lng": 0}

    return {
        "lat": ubicacion.lat,
        "lng": ubicacion.lng
    }

# ======================
# HISTORIAL
# ======================

@router.get("/historial/cliente")
def historial_cliente(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return db.query(Viaje).filter(
        Viaje.cliente_id == current_user.id,
        Viaje.estado == "finalizado"
    ).all()

@router.get("/historial/conductor")
def historial_conductor(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Viaje).filter(
        Viaje.conductor_id == current_user.id,
        Viaje.estado == "finalizado"
    ).all()

@router.get("/ubicacion_conductor/{viaje_id}")
def obtener_ubicacion_conductor(
    viaje_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):

    from datetime import timedelta
    limite = datetime.utcnow() - timedelta(seconds=20)

    ubicacion = db.query(Ubicacion).filter(
        Ubicacion.viaje_id == viaje_id,
        Ubicacion.updated_at >= limite
    ).order_by(
        Ubicacion.updated_at.desc()
    ).first()

    if not ubicacion:
        return {"lat": 0, "lng": 0}

    return {
        "lat": ubicacion.lat,
        "lng": ubicacion.lng
    }

@router.get("/mis_viajes_cliente")
def get_mis_viajes_cliente(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    viajes = db.query(Viaje).filter(
        Viaje.cliente_id == current_user.id,
        Viaje.estado.notin_(["finalizado", "cancelado"])
    ).all()

    return [
        {
            "id": v.id,
            "estado": v.estado,
            "lat_origen": v.lat_origen,
            "lng_origen": v.lng_origen,
            "lat_destino": v.lat_destino,
            "lng_destino": v.lng_destino,
            "lat_conductor": getattr(v, 'lat_conductor', None),
            "lng_conductor": getattr(v, 'lng_conductor', None)
        }
        for v in viajes
    ]

@router.get("/ruta")
def obtener_ruta(
    lat1: float,
    lng1: float,
    lat2: float,
    lng2: float,
    current_user: Usuario = Depends(get_current_user)
):

    ruta = obtener_ruta_google(lat1, lng1, lat2, lng2)

    if not ruta:
        return {"error": "No se pudo calcular ruta"}

    return ruta

@router.post("/cancelar_viaje")
def cancelar_viaje(
    data: CancelarViajeRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    viaje = db.query(Viaje).filter(Viaje.id == data.viaje_id).first()

    if not viaje:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")

    # 🔒 Validar participación
    if current_user.id not in [viaje.cliente_id, viaje.conductor_id]:
        raise HTTPException(status_code=403, detail="No autorizado")

    # 🔒 Validar transición
    if not puede_transicionar(viaje.estado, "cancelado"):
        raise HTTPException(
            status_code=400,
            detail=f"No se puede cancelar en estado {viaje.estado}"
        )

    actualizar_estado_viaje(db, viaje, "cancelado")

    firebase_db.reference(f"viajes_activos/{viaje.id}").delete()

    return {"mensaje": "Viaje cancelado"}

def detectar_ciudad(db, lat, lng):

    ciudades = db.execute(text("""

        SELECT
            id,
            nombre,
            lat,
            lng,
            radio_km

        FROM ciudades

        WHERE activa = true

    """)).mappings().all()

    ciudad_detectada = None
    menor_distancia = 999999999

    for c in ciudades:

        distancia = calcular_distancia_metros(
            float(lat),
            float(lng),
            float(c["lat"]),
            float(c["lng"])
        ) / 1000

        if distancia <= c["radio_km"]:

            if distancia < menor_distancia:

                menor_distancia = distancia
                ciudad_detectada = c

    return ciudad_detectada

@router.post("/actualizar_ubicacion_disponible")
def actualizar_ubicacion_disponible(
    data: UbicacionConductorRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):

    if current_user.rol != "conductor":
        raise HTTPException(403, "Solo conductores")

    ubicacion = db.query(Ubicacion).filter(
        Ubicacion.conductor_id == current_user.id,
        Ubicacion.viaje_id == None
    ).order_by(
        Ubicacion.updated_at.desc()
    ).first()

    if ubicacion:

        ubicacion.lat = data.lat
        ubicacion.lng = data.lng
        ubicacion.updated_at = datetime.utcnow()

    else:

        ubicacion = Ubicacion(
            conductor_id=current_user.id,
            viaje_id=None,
            lat=data.lat,
            lng=data.lng,
            updated_at=datetime.utcnow()
        )

        db.add(ubicacion)

    # ======================
    # DETECTAR CIUDAD
    # ======================

    ciudad = detectar_ciudad(
        db,
        data.lat,
        data.lng
    )

    if ciudad:

        current_user.ciudad_id = ciudad["id"]

        current_user.ciudad = ciudad["nombre"]

        ubicacion.ciudad_id = ciudad["id"]

    db.commit()

    return {"ok": True}
