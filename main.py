import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ======================
# ENV
# ======================
load_dotenv()

# ======================
# IMPORTS
# ======================
from database import Base, engine
from routers import usuarios, viajes, ofertas, chat, evaluaciones

# ======================
# CONFIG
# ======================
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# ======================
# FIREBASE (OPCIONAL)
# ======================
try:
    import firebase_admin
    from firebase_admin import credentials

    firebase_path = os.getenv("FIREBASE_CREDENTIALS")
    firebase_url = os.getenv("FIREBASE_DB_URL")

    if firebase_path and firebase_url and os.path.exists(firebase_path):
        cred = credentials.Certificate(firebase_path)

        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred, {
                "databaseURL": firebase_url
            })

        print("🔥 Firebase inicializado")

    else:
        print("⚠️ Firebase desactivado (no configurado)")

except Exception as e:
    print(f"❌ Firebase error: {e}")

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
    allow_origins=origins.split(",") if origins != "*" else ["*"],
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

# ======================
# TEST
# ======================
@app.get("/")
def root():
    return {"ok": True, "mensaje": "Movara API funcionando 🚀"}