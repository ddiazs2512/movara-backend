from pydantic import BaseModel, validator
from typing import Optional
import re

# =========================
# USUARIOS
# =========================

class UsuarioCreate(BaseModel):
    telefono: str
    password: str
    nombre: str

    @validator("telefono")
    def validar_telefono(cls, v):
        if not re.match(r"^9\d{8}$", v):
            raise ValueError("El teléfono debe tener 9 dígitos y empezar con 9")
        return v

    @validator("password")
    def validar_password(cls, v):
        if len(v) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")
        return v

    @validator("nombre")
    def validar_nombre(cls, v):
        if len(v.strip()) < 2:
            raise ValueError("Nombre muy corto")
        return v


class UsuarioLogin(BaseModel):
    telefono: str
    password: str


# =========================
# VIAJES
# =========================

class ViajeCreate(BaseModel):
    cliente_id: int
    origen: str
    destino: str
    precio_propuesto: float

    lat_origen: float
    lng_origen: float
    lat_destino: float
    lng_destino: float


# =========================
# OFERTAS (LEGACY - mantener por compatibilidad)
# =========================

class CrearOferta(BaseModel):
    viaje_id: int
    conductor_id: int
    precio: float


class AceptarOferta(BaseModel):
    oferta_id: int


# =========================
# CONDUCTOR
# =========================

class ConductorCreate(BaseModel):
    usuario_id: int
    dni: str
    placa: str
    color_vehiculo: str
    modelo: str
    marca: str
    anio: int
    licencia: str

class ResponderOfertaRequest(BaseModel):
    viaje_id: int
    usuario_id: int
    precio: float
    accion: str
    conductor_id: Optional[int] = None  # 🔥 NUEVO (NO rompe nada)

# =========================
# 🔥 NUEVO SISTEMA (CRÍTICO)
# =========================

class TripActionRequest(BaseModel):
    viaje_id: int
    usuario_id: int
    usuario_rol: str  # "cliente" o "conductor"
    accion: str       # "ofertar", "contraofertar", "aceptar", "iniciar", "finalizar"
    precio: Optional[float] = None


class ViajeResponse(BaseModel):
    id: int

    cliente_id: Optional[int]
    conductor_id: Optional[int]

    lat_origen: float
    lng_origen: float
    lat_destino: float
    lng_destino: float

    lat_conductor: Optional[float]
    lng_conductor: Optional[float]

    referencia_recojo: Optional[str]
    destino_referencia: Optional[str]

    precio_acordado: Optional[float]

    conductor_nombre: Optional[str]
    conductor_telefono: Optional[str]

    cliente_nombre: Optional[str]
    cliente_telefono: Optional[str]

    marca: Optional[str]
    modelo: Optional[str]
    color_vehiculo: Optional[str]
    placa: Optional[str]
    
class RutaResponse(BaseModel):
    distancia_texto: Optional[str]
    duracion_texto: Optional[str]
    polyline: Optional[str]


class ViajeActivoResponse(BaseModel):
    activo: bool

    id: Optional[int]
    estado: Optional[str]

    lat_origen: Optional[float]
    lng_origen: Optional[float]

    lat_destino: Optional[float]
    lng_destino: Optional[float]

    lat_conductor: Optional[float]
    lng_conductor: Optional[float]

    referencia_recojo: Optional[str]
    destino_referencia: Optional[str]

    cliente_id: Optional[int]
    cliente_nombre: Optional[str]
    cliente_telefono: Optional[str]

    conductor_id: Optional[int]
    conductor_nombre: Optional[str]
    conductor_telefono: Optional[str]

    # NUEVOS
    precio_cliente: Optional[float]
    cliente_rating: Optional[float]
    cliente_total_viajes: Optional[int]
    ruta: Optional[RutaResponse]

    precio_acordado: Optional[float]

    ofertas: list = []

    marca: Optional[str]
    modelo: Optional[str]
    color_vehiculo: Optional[str]
    placa: Optional[str]
