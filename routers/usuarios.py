from fastapi import APIRouter, Header, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
import bcrypt
from fastapi.security import OAuth2PasswordBearer

from auth import verify_token, create_access_token
from models import Usuario, Conductor, FCMToken
from database import get_db
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

router = APIRouter()

def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    if not token:
        raise HTTPException(status_code=401, detail="Token faltante")

    # 🔥 SOPORTAR "Bearer xxx"
    if token.startswith("Bearer "):
        token = token.split(" ")[1]

    payload = verify_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")

    user_id = payload.get("user_id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido")

    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()

    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    return usuario

# ======================
# SCHEMAS
# ======================

class UsuarioCreate(BaseModel):
    telefono: str
    password: str
    nombre: str

class UsuarioLogin(BaseModel):
    telefono: str
    password: str

class TokenRequest(BaseModel):
    token: str

# ======================
# REGISTER
# ======================

@router.post("/register")
def register(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db)
):

    existente = db.query(Usuario).filter(Usuario.telefono == usuario.telefono).first()
    if existente:
        raise HTTPException(400, "Teléfono ya registrado")

    hashed = bcrypt.hashpw(usuario.password.encode("utf-8"), bcrypt.gensalt(rounds=10)).decode("utf-8")

    nuevo = Usuario(
        telefono=usuario.telefono,
        nombre=usuario.nombre,
        hashed_password=hashed,
        rol="cliente",
        modo_actual="cliente",
        activo=False
    )

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return {"usuario_id": nuevo.id}

# ======================
# LOGIN
# ======================

import uuid

from auth import create_access_token

@router.post("/login")
def login(usuario: UsuarioLogin, db: Session = Depends(get_db)):

    user = db.query(Usuario).filter(
        Usuario.telefono == usuario.telefono
    ).first()

    if not user:
        raise HTTPException(404, "Usuario no encontrado")

    if not bcrypt.checkpw(
        usuario.password.encode("utf-8"),
        user.hashed_password.encode("utf-8")
    ):
        raise HTTPException(400, "Contraseña incorrecta")

    access_token = create_access_token({
        "user_id": user.id,
        "rol": user.rol
    })

    return {
        "usuario_id": user.id,
        "rol": user.rol,
        "nombre": user.nombre,
        "modo": user.modo_actual,
        "token": access_token
    }

# ======================
# OBTENER USUARIO
# ======================

@router.get("/usuario")
def get_usuario(
    user: Usuario = Depends(get_current_user)
):

    return {
        "id": user.id,
        "nombre": user.nombre
    }

# ======================
# CONVERTIR CONDUCTOR
# ======================

@router.post("/convertir_conductor")
def convertir_conductor(
    dni: str,
    placa: str,
    modelo: str,
    marca: str,
    color: str,
    anio: int,
    licencia: str,
    user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    existente = db.query(Conductor).filter(
        Conductor.usuario_id == user.id
    ).first()

    if existente:
        raise HTTPException(400, "Ya eres conductor")

    conductor = Conductor(
        usuario_id=user.id,
        dni=dni,
        placa=placa,
        modelo=modelo,
        marca=marca,
        color_vehiculo=color,
        anio=anio,
        licencia=licencia
    )

    db.add(conductor)
    user.rol = "conductor"
    user.modo_actual = "conductor"
    user.activo = True
    db.commit()

    return {"mensaje": "Ahora eres conductor"}

# ======================
# RECUPERAR PASSWORD
# ======================

@router.post("/recuperar_password")
def recuperar_password(telefono: str):
    return {"mensaje": "Código enviado"}

# ======================
# VERIFICAR CÓDIGO
# ======================

@router.post("/verificar_codigo")
def verificar_codigo(telefono: str, codigo: str):
    return {"mensaje": "Código verificado"}

# ======================
# CAMBIAR PASSWORD
# ======================

@router.post("/cambiar_password")
def cambiar_password(
    telefono: str,
    nueva_password: str,
    db: Session = Depends(get_db)
):
        
        usuario = db.query(Usuario).filter(Usuario.telefono == telefono).first()

        if not usuario:
            raise HTTPException(404, "Usuario no encontrado")

        hashed = bcrypt.hashpw(nueva_password.encode(), bcrypt.gensalt()).decode()
        usuario.hashed_password = hashed

        db.commit()

        return {"mensaje": "Contraseña actualizada"}
    
# ======================
# CAMBIAR MODO
# ======================

@router.post("/cambiar_modo")
def cambiar_modo(
    modo: str,
    user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    usuario = user

    if modo not in ["cliente", "conductor"]:
        raise HTTPException(400, "Modo inválido")

    if modo == "conductor":
        conductor = db.query(Conductor).filter(
            Conductor.usuario_id == user.id
        ).first()

        if not conductor:
            raise HTTPException(403, "Debes registrarte como conductor")

    usuario.modo_actual = modo
    usuario.activo = True

    db.commit()

    return {
        "mensaje": "Modo actualizado",
        "modo": usuario.modo_actual
    }

# ======================
# GUARDAR TOKEN
# ======================

@router.post("/guardar_token")
def guardar_token(
    data: TokenRequest,
    user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    if not user.activo:
        return {"mensaje": "Usuario inactivo"}

    db.query(FCMToken).filter(
        FCMToken.usuario_id == user.id
    ).delete()

    nuevo = FCMToken(
        usuario_id=user.id,
        token=data.token
    )

    db.add(nuevo)
    db.commit()

    return {"mensaje": "Token guardado"}


# ======================
# ACTIVAR CONDUCTOR
# ======================

@router.post("/conductor/activar")
def activar_conductor(
    user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    if user.rol != "conductor":
        raise HTTPException(403, "No autorizado")

    user.activo = True
    db.commit()

    return {"mensaje": "Conductor activo"}

# ======================
# DESACTIVAR CONDUCTOR
# ======================

@router.post("/conductor/desactivar")
def desactivar_conductor(
    user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # 🔐 Validación básica de rol (opcional pero recomendable)
    if user.rol != "conductor":
        raise HTTPException(403, "No autorizado")

    user.activo = False
    db.commit()

    return {"mensaje": "Conductor desactivado"}

@router.post("/session/login")
def session_login(
    token: str,
    ciudad: str,
    user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    try:

        db.query(FCMToken).filter(
            FCMToken.usuario_id == user.id
        ).delete()

        db.query(FCMToken).filter(
            FCMToken.token == token
        ).delete()

        nuevo_token = FCMToken(
            usuario_id=user.id,
            token=token
        )
        db.add(nuevo_token)

        user.activo = True
        user.ciudad = ciudad

        db.commit()

        return {"mensaje": "Sesión iniciada"}

    except Exception as e:
        print("❌ ERROR LOGIN SESSION:", e)
        raise HTTPException(500, "Error iniciando sesión")

@router.post("/logout")
def logout(
    user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    print("🧪 LOGOUT usuario_id:", user.id)

    try:
        db.query(FCMToken).filter(
            FCMToken.usuario_id == user.id
        ).delete()

        user.activo = False

        db.commit()

        print(f"🚪 Usuario {user.id} deslogueado")

        return {"mensaje": "Logout exitoso"}

    except Exception as e:
        print("❌ ERROR LOGOUT:", e)
        raise HTTPException(500, "Error cerrando sesión")
