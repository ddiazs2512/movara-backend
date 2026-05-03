from pydantic import BaseModel


class UsuarioCreate(BaseModel):

    nombre: str
    telefono: str
    password: str
    rol: str


class UsuarioLogin(BaseModel):

    telefono: str
    password: str