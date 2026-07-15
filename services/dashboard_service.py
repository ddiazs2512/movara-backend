from sqlalchemy.orm import Session
from sqlalchemy import func

from admin_models import (
    Usuario,
    Conductor,
    Viaje,
    EstadoViaje
)


class DashboardService:

    @staticmethod
    def obtener_resumen(db: Session):

        usuarios = db.query(func.count(Usuario.id)).scalar()

        conductores = db.query(func.count(Conductor.id)).scalar()

        viajes_activos = (
            db.query(func.count(Viaje.id))
            .filter(
                Viaje.estado.in_([
                    EstadoViaje.OFERTA.value,
                    EstadoViaje.ASIGNADO.value,
                    EstadoViaje.EN_CAMINO.value,
                    EstadoViaje.LLEGADO.value,
                    EstadoViaje.EN_CURSO.value
                ])
            )
            .scalar()
        )

        viajes_finalizados = (
            db.query(func.count(Viaje.id))
            .filter(
                Viaje.estado == EstadoViaje.FINALIZADO.value
            )
            .scalar()
        )

        return {

            "usuarios": usuarios,

            "conductores": conductores,

            "viajes_activos": viajes_activos,

            "viajes_finalizados": viajes_finalizados

        }
