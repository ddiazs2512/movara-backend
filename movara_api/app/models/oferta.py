from sqlalchemy import Column, Integer, Float, ForeignKey, String
from app.database import Base


class Oferta(Base):

    __tablename__ = "ofertas"

    id = Column(Integer, primary_key=True, index=True)

    viaje_id = Column(Integer, ForeignKey("viajes.id"))

    conductor_id = Column(Integer, ForeignKey("usuarios.id"))

    precio_ofrecido = Column(Float)

    estado = Column(String, default="activa")