@echo off

mkdir movara_api
cd movara_api

mkdir app
mkdir app\models
mkdir app\schemas
mkdir app\routes
mkdir app\services
mkdir app\realtime
mkdir app\security

echo from fastapi import FastAPI> app\main.py
echo from app.routes import auth, viajes>> app\main.py
echo.>> app\main.py
echo app = FastAPI()>> app\main.py
echo.>> app\main.py
echo app.include_router(auth.router)>> app\main.py
echo app.include_router(viajes.router)>> app\main.py

echo from sqlalchemy import create_engine> app\database.py
echo from sqlalchemy.orm import sessionmaker, declarative_base>> app\database.py
echo.>> app\database.py
echo DATABASE_URL = "sqlite:///movara.db">> app\database.py
echo.>> app\database.py
echo engine = create_engine(DATABASE_URL)>> app\database.py
echo SessionLocal = sessionmaker(bind=engine)>> app\database.py
echo Base = declarative_base()>> app\database.py

echo.> app\config.py

echo from sqlalchemy import Column, Integer, String> app\models\usuario.py
echo from app.database import Base>> app\models\usuario.py
echo.>> app\models\usuario.py
echo class Usuario(Base):>> app\models\usuario.py
echo     __tablename__ = "usuarios">> app\models\usuario.py
echo.>> app\models\usuario.py
echo     id = Column(Integer, primary_key=True)>> app\models\usuario.py
echo     nombre = Column(String)>> app\models\usuario.py
echo     telefono = Column(String)>> app\models\usuario.py
echo     rol = Column(String)>> app\models\usuario.py

echo.> app\models\vehiculo.py
echo.> app\models\viaje.py
echo.> app\models\oferta.py
echo.> app\models\movimiento.py

echo.> app\schemas\usuario_schema.py
echo.> app\schemas\viaje_schema.py
echo.> app\schemas\oferta_schema.py

echo from fastapi import APIRouter> app\routes\auth.py
echo router = APIRouter()>> app\routes\auth.py
echo.>> app\routes\auth.py
echo @router.get("/login")>> app\routes\auth.py
echo def login():>> app\routes\auth.py
echo     return {"mensaje": "login ok"}>> app\routes\auth.py

echo from fastapi import APIRouter> app\routes\viajes.py
echo router = APIRouter()>> app\routes\viajes.py
echo.>> app\routes\viajes.py
echo @router.get("/viajes")>> app\routes\viajes.py
echo def viajes():>> app\routes\viajes.py
echo     return {"mensaje": "lista de viajes"}>> app\routes\viajes.py

echo.> app\routes\ubicacion.py
echo.> app\services\matching_service.py
echo.> app\services\precio_service.py
echo.> app\realtime\websocket_manager.py
echo.> app\security\jwt_handler.py

echo fastapi> requirements.txt
echo uvicorn>> requirements.txt
echo sqlalchemy>> requirements.txt

echo import uvicorn> run.py
echo uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)>> run.py

echo.
echo Backend Movara creado correctamente
pause