from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime

from database import Base


class Admin(Base):

    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String, unique=True, nullable=False)

    hashed_password = Column(String, nullable=False)

    activo = Column(Boolean, default=True)

    fecha_creacion = Column(
        DateTime,
        default=datetime.utcnow
    )
