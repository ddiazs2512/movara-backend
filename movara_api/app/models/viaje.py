from sqlalchemy import Column, Integer, String, Float, ForeignKey
from app.database import Base


class Viaje(Base):

    __tablename__ = "viajes"

    id = Column(Integer, primary_key=True, index=True)

    cliente_id = Column(Integer, ForeignKey("usuarios.id"))

    conductor_id = Column(Integer, nullable=True)

    origen = Column(String)

    destino = Column(String)

    referencia_recojo = Column(String)

    lat_origen = Column(Float)

    lng_origen = Column(Float)

    lat_destino = Column(Float)

    lng_destino = Column(Float)

    precio_cliente = Column(Float)

    precio_conductor = Column(Float, nullable=True)

    precio_acordado = Column(Float, nullable=True)

    estado = Column(String, default="oferta_cliente")