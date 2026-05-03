from sqlalchemy import Column, Integer, String, Boolean, Float
from app.database import Base


class Usuario(Base):

    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)

    nombre = Column(String, nullable=False)

    telefono = Column(String, unique=True, nullable=False)

    password = Column(String, nullable=False)

    rol = Column(String)  # cliente o conductor

    disponible = Column(Boolean, default=False)

    latitud = Column(Float, nullable=True)

    longitud = Column(Float, nullable=True)

    rating = Column(Float, default=5)