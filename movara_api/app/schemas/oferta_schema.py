from pydantic import BaseModel


class OfertaCreate(BaseModel):

    viaje_id: int

    conductor_id: int

    precio_ofrecido: float