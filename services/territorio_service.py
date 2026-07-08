from sqlalchemy.orm import Session

from models import (
    AreaOperacion,
    AreaOperacionDistrito
)


class TerritorioService:

    @staticmethod
    def listar_areas(db: Session):

        return (
            db.query(AreaOperacion)
            .order_by(AreaOperacion.nombre)
            .all()
        )

    @staticmethod
    def obtener_area(
        db: Session,
        area_id: int
    ):

        return (
            db.query(AreaOperacion)
            .filter(
                AreaOperacion.id == area_id
            )
            .first()
        )

    @staticmethod
    def crear_area(
        db: Session,
        codigo: str,
        nombre: str,
        descripcion: str,
        radio_operacion: int,
        latitud: float,
        longitud: float
    ):

        area = AreaOperacion(

            codigo=codigo,

            nombre=nombre,

            descripcion=descripcion,

            radio_operacion=radio_operacion,

            latitud_centro=latitud,

            longitud_centro=longitud
        )

        db.add(area)

        db.commit()

        db.refresh(area)

        return area

    @staticmethod
    def listar_distritos_area(
        db: Session,
        area_id: int
    ):

        return (
            db.query(AreaOperacionDistrito)
            .filter(
                AreaOperacionDistrito.area_operacion_id == area_id
            )
            .all()
        )

    @staticmethod
    def asignar_distrito(
        db: Session,
        area_id: int,
        distrito_id: int
    ):

        existe = (
            db.query(AreaOperacionDistrito)
            .filter(
                AreaOperacionDistrito.area_operacion_id == area_id,
                AreaOperacionDistrito.distrito_id == distrito_id
            )
            .first()
        )

        if existe:
            return existe

        relacion = AreaOperacionDistrito(

            area_operacion_id=area_id,

            distrito_id=distrito_id
        )

        db.add(relacion)

        db.commit()

        db.refresh(relacion)

        return relacion
