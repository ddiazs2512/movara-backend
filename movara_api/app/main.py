from fastapi import FastAPI

from app.routes import auth
from app.routes import viajes
from app.routes import ubicacion

from app.database import Base, engine

from app.models.usuario import Usuario
from app.models.viaje import Viaje
from app.models.oferta import Oferta

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router)

app.include_router(viajes.router)

app.include_router(ubicacion.router)