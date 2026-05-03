from pydantic import BaseModel


class ViajeCreate(BaseModel):

    cliente_id: int

    origen: str
    destino: str

    referencia_recojo: str

    lat_origen: float
    lng_origen: float

    lat_destino: float
    lng_destino: float

    precio_cliente: float