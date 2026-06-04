import os
import logging
from fastapi import FastAPI

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from routers import usuarios, viajes, ofertas, chat, evaluaciones
from routers import websocket

import firebase_admin
from firebase_admin import credentials

# ======================
# CONFIG INICIAL
# ======================
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# ======================
# FIREBASE
# ======================
firebase_path = os.getenv("FIREBASE_CREDENTIALS")
firebase_url = os.getenv("FIREBASE_DB_URL")

if not firebase_path or not firebase_url:
    raise Exception("Faltan variables FIREBASE en .env")

cred = credentials.Certificate(firebase_path)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        "databaseURL": firebase_url
    })

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
app.include_router(
    websocket.router
)

# ======================
# TEST
# ======================
@app.get("/")
def root():
    return {"ok": True, "mensaje": "Movara API funcionando 🚀"}
