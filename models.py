from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float
from datetime import datetime
from database import Base
from sqlalchemy.orm import relationship
from enum import Enum

# ======================
# STATE MACHINE VIAJE
# ======================

ESTADOS_VALIDOS = {
    "oferta",
    "asignado",
    "en_camino",
    "llegado",
    "en_curso",
    "finalizado",
    "cancelado"
}

TRANSICIONES_VALIDAS = {
    "oferta": {"asignado", "cancelado"},
    "asignado": {"en_camino", "cancelado"},
    "en_camino": {"llegado", "cancelado"},
    "llegado": {"en_curso", "cancelado"},
    "en_curso": {"finalizado"},
    "finalizado": set(),
    "cancelado": set()
}


def puede_transicionar(estado_actual: str, nuevo_estado: str) -> bool:
    if estado_actual not in TRANSICIONES_VALIDAS:
        return False
    return nuevo_estado in TRANSICIONES_VALIDAS[estado_actual]

class EstadoViaje(str, Enum):
    OFERTA = "oferta"
    ASIGNADO = "asignado"
    EN_CAMINO = "en_camino"
    LLEGADO = "llegado"
    EN_CURSO = "en_curso"
    FINALIZADO = "finalizado"
    CANCELADO = "cancelado"

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    telefono = Column(String, unique=True, nullable=False, index=True)
    ciudad = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    rol = Column(String, nullable=False)  # cliente / conductor

    # Estados
    activo = Column(Boolean, default=False)
    token = Column(String, unique=True, index=True)
    disponible = Column(Boolean, default=True)
    modo_actual = Column(String, default="cliente")

    # Finanzas
    saldo = Column(Float, default=0.0)
    deuda = Column(Float, default=0.0)
    rating = Column(Float, default=5.0)
    total_viajes = Column(Integer, default=0)

    # Relaciones con evaluaciones
    evaluaciones_recibidas = relationship(
        "Evaluacion",
        foreign_keys="[Evaluacion.evaluado_id]",
        backref="evaluado"
    )

    evaluaciones_realizadas = relationship(
        "Evaluacion",
        foreign_keys="[Evaluacion.evaluador_id]",
        backref="evaluador"
    )


class Viaje(Base):
    __tablename__ = "viajes"

    id = Column(Integer, primary_key=True, index=True)

    # 🔥 PRIMERO COLUMNAS
    cliente_id = Column(Integer, ForeignKey("usuarios.id"))
    conductor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

    # 🔥 DESPUÉS RELACIONES
    cliente = relationship(
        "Usuario",
        foreign_keys=[cliente_id]
    )

    conductor = relationship(
        "Usuario",
        foreign_keys=[conductor_id]
    )

    referencia_recojo = Column(String, nullable=False)
    destino_referencia = Column(String, nullable=False)

    lat_origen = Column(Float, nullable=False)
    lng_origen = Column(Float, nullable=False)
    lat_destino = Column(Float, nullable=False)
    lng_destino = Column(Float, nullable=False)
    lat_conductor = Column(Float, nullable=True)
    lng_conductor = Column(Float, nullable=True) 

    distancia_km = Column(Float, nullable=True)

    precio_cliente_1 = Column(Float, nullable=False)
    precio_conductor = Column(Float, nullable=True)
    precio_cliente_2 = Column(Float, nullable=True)
    precio_acordado = Column(Float, nullable=True)

    comision_app = Column(Float, nullable=True)
    ganancia_conductor = Column(Float, nullable=True)
    ciudad = Column(String, nullable=True)

    estado = Column(String, default=EstadoViaje.OFERTA.value, index=True)

    ultimo_en_ofertar = Column(String(20), nullable=True)

    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_ultima_accion = Column(DateTime, default=datetime.utcnow)

    fecha_inicio = Column(DateTime, nullable=True)
    fecha_fin = Column(DateTime, nullable=True)

    evaluaciones = relationship("Evaluacion", backref="viaje")


class Conductor(Base):
    __tablename__ = "conductores"

    id = Column(Integer, primary_key=True, index=True)

    usuario_id = Column(Integer, ForeignKey("usuarios.id"), unique=True, nullable=False)

    dni = Column(String, nullable=False)
    placa = Column(String, nullable=False)
    color_vehiculo = Column(String, nullable=False)
    modelo = Column(String, nullable=False)

    marca = Column(String, nullable=True)
    anio = Column(Integer, nullable=True)
    licencia = Column(String, nullable=True)
    foto = Column(String, nullable=True)

    verificado = Column(Boolean, default=False)
    disponible = Column(Boolean, default=False)


class Oferta(Base):
    __tablename__ = "ofertas"

    id = Column(Integer, primary_key=True, index=True)
    viaje_id = Column(Integer, ForeignKey("viajes.id"))
    conductor_id = Column(Integer, ForeignKey("usuarios.id"))

    precio = Column(Float, nullable=False)
    estado = Column(String, default="activa")  # activa / aceptada / rechazada

    fecha_creacion = Column(DateTime, default=datetime.utcnow)


class Evaluacion(Base):
    __tablename__ = "evaluaciones"

    id = Column(Integer, primary_key=True, index=True)

    viaje_id = Column(Integer, ForeignKey("viajes.id"))
    evaluador_id = Column(Integer, ForeignKey("usuarios.id"))
    evaluado_id = Column(Integer, ForeignKey("usuarios.id"))

    rol_evaluado = Column(String)
    estrellas = Column(Integer)
    comentario = Column(String, nullable=True)

    fecha = Column(DateTime, default=datetime.utcnow)


class Mensaje(Base):
    __tablename__ = "mensajes"

    id = Column(Integer, primary_key=True, index=True)
    viaje_id = Column(Integer, ForeignKey("viajes.id"))
    emisor_id = Column(Integer, ForeignKey("usuarios.id"))
    receptor_id = Column(Integer, ForeignKey("usuarios.id"))
    mensaje = Column(String)
    fecha = Column(DateTime, default=datetime.utcnow)
    leido = Column(Boolean, default=False)


class FCMToken(Base):
    __tablename__ = "fcm_tokens"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), index=True)
    token = Column(String, index=True)  # 🔥 quitamos unique=True para permitir múltiples dispositivos

class Ubicacion(Base):
    __tablename__ = "ubicaciones"

    id = Column(Integer, primary_key=True)
    viaje_id = Column(Integer)
    conductor_id = Column(Integer)
    lat = Column(Float)
    lng = Column(Float)