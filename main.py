import os
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from routers import usuarios, viajes, ofertas, chat, evaluaciones
from routers import admin_territorio

import firebase_admin
from firebase_admin import credentials

from websocket.mercado_ws import router as mercado_router
from websocket.mis_viajes_ws import router as mis_viajes_router
from routers import admin_configuracion
from routers import places
from routers import reverse_geocode

# ======================
# CONFIG INICIAL
# ======================
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# ======================
# FIREBASE
# ======================
firebase_path = os.getenv("FIREBASE_CREDENTIALS")

if not firebase_path:
    raise Exception("Falta FIREBASE_CREDENTIALS")

cred = credentials.Certificate(firebase_path)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

# ======================
# DB
# ======================
Base.metadata.create_all(bind=engine)

# ======================
# CORS
# ======================
origins = os.getenv("CORS_ORIGINS", "*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================
# ROUTERS
# ======================
app.include_router(usuarios.router)
app.include_router(viajes.router)
app.include_router(ofertas.router)
app.include_router(chat.router)
app.include_router(evaluaciones.router)
app.include_router(mercado_router)
app.include_router(mis_viajes_router)
app.include_router(places.router)
app.include_router(
    admin_configuracion.router
)
app.include_router(
    admin_territorio.router
)
app.include_router(reverse_geocode.router)


# ======================
# TEST
# ======================
@app.get("/")
def root():
    return {"ok": True, "mensaje": "Movara API funcionando 🚀"}
