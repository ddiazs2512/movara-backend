from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.usuario import Usuario
from app.schemas.usuario_schema import UsuarioCreate, UsuarioLogin


router = APIRouter()


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.post("/register")

def register(usuario: UsuarioCreate, db: Session = Depends(get_db)):

    existente = db.query(Usuario).filter(
        Usuario.telefono == usuario.telefono
    ).first()

    if existente:

        raise HTTPException(
            status_code=400,
            detail="Teléfono ya registrado"
        )

    nuevo = Usuario(

        nombre=usuario.nombre,
        telefono=usuario.telefono,
        password=usuario.password,
        rol=usuario.rol

    )

    db.add(nuevo)

    db.commit()

    db.refresh(nuevo)

    return {"usuario_id": nuevo.id}


@router.post("/login")

def login(usuario: UsuarioLogin, db: Session = Depends(get_db)):

    user = db.query(Usuario).filter(
        Usuario.telefono == usuario.telefono
    ).first()

    if not user:

        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )

    if user.password != usuario.password:

        raise HTTPException(
            status_code=400,
            detail="Contraseña incorrecta"
        )

    return {
        "usuario_id": user.id,
        "rol": user.rol
    }