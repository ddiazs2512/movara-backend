from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from models import Viaje
from routers.viajes import actualizar_estado_viaje
from services.configuracion_service import ConfiguracionService

class ViajeMaintenanceService:

    @staticmethod
    def ejecutar(db: Session):

        ViajeMaintenanceService.revisar_ofertas(db)
        ViajeMaintenanceService.revisar_asignados(db)
        ViajeMaintenanceService.revisar_en_camino(db)
        ViajeMaintenanceService.revisar_llegados(db)
        ViajeMaintenanceService.revisar_en_curso(db)

    @staticmethod
    def revisar_ofertas(db: Session):
    
        timeout = ConfiguracionService.obtener_int(
            db,
            "viajes",
            "oferta_timeout"
        )
    
        viajes = db.query(Viaje).filter(
            Viaje.estado == "oferta"
        ).all()
    
        cancelados = 0
    
        for viaje in viajes:
    
            if viaje.fecha_creacion is None:
                continue
    
            tiempo = datetime.utcnow() - viaje.fecha_creacion
    
            if tiempo >= timedelta(minutes=timeout):
    
                print(
                    f"[MANTENIMIENTO] "
                    f"Cancelando viaje {viaje.id} "
                    f"por timeout ({timeout} min)"
                )
    
                actualizar_estado_viaje(
                    db,
                    viaje,
                    "cancelado"
                )
    
                cancelados += 1
    
        if cancelados:
    
            print(
                f"[MANTENIMIENTO] "
                f"Ofertas canceladas: {cancelados}"
            )

    @staticmethod
    def revisar_asignados(db: Session):
    
        timeout = ConfiguracionService.obtener_int(
            db,
            "viajes",
            "asignado_timeout"
        )
    
        viajes = db.query(Viaje).filter(
            Viaje.estado == "asignado"
        ).all()
    
        cancelados = 0
    
        for viaje in viajes:
    
            if viaje.fecha_ultima_accion is None:
                continue
    
            tiempo = datetime.utcnow() - viaje.fecha_ultima_accion
    
            if tiempo >= timedelta(minutes=timeout):
    
                print(
                    f"[MANTENIMIENTO] "
                    f"Cancelando viaje {viaje.id} "
                    f"(asignado)"
                )
    
                actualizar_estado_viaje(
                    db,
                    viaje,
                    "cancelado"
                )
    
                cancelados += 1
    
        if cancelados:
    
            print(
                f"[MANTENIMIENTO] "
                f"Asignados cancelados: {cancelados}"
            )

    @staticmethod
    def revisar_en_camino(db: Session):
    
        timeout = ConfiguracionService.obtener_int(
            db,
            "viajes",
            "en_camino_timeout"
        )
    
        viajes = db.query(Viaje).filter(
            Viaje.estado == "en_camino"
        ).all()
    
        cancelados = 0
    
        for viaje in viajes:
    
            if viaje.fecha_ultima_accion is None:
                continue
    
            tiempo = datetime.utcnow() - viaje.fecha_ultima_accion
    
            if tiempo >= timedelta(minutes=timeout):
    
                print(
                    f"[MANTENIMIENTO] "
                    f"Cancelando viaje {viaje.id} "
                    f"(en_camino)"
                )
    
                actualizar_estado_viaje(
                    db,
                    viaje,
                    "cancelado"
                )
    
                cancelados += 1
    
        if cancelados:
    
            print(
                f"[MANTENIMIENTO] "
                f"En camino cancelados: {cancelados}"
            )

    @staticmethod
    def revisar_llegados(db: Session):
    
        timeout = ConfiguracionService.obtener_int(
            db,
            "viajes",
            "llegado_timeout"
        )
    
        viajes = db.query(Viaje).filter(
            Viaje.estado == "llegado"
        ).all()
    
        cancelados = 0
    
        for viaje in viajes:
    
            if viaje.fecha_ultima_accion is None:
                continue
    
            tiempo = datetime.utcnow() - viaje.fecha_ultima_accion
    
            if tiempo >= timedelta(minutes=timeout):
    
                print(
                    f"[MANTENIMIENTO] "
                    f"Cancelando viaje {viaje.id} "
                    f"(llegado)"
                )
    
                actualizar_estado_viaje(
                    db,
                    viaje,
                    "cancelado"
                )
    
                cancelados += 1
    
        if cancelados:
    
            print(
                f"[MANTENIMIENTO] "
                f"Llegados cancelados: {cancelados}"
            )

    @staticmethod
    def revisar_en_curso(db: Session):
    
        timeout = ConfiguracionService.obtener_int(
            db,
            "viajes",
            "en_curso_timeout"
        )
    
        viajes = db.query(Viaje).filter(
            Viaje.estado == "en_curso"
        ).all()
    
        for viaje in viajes:
    
            if viaje.fecha_ultima_accion is None:
                continue
    
            tiempo = datetime.utcnow() - viaje.fecha_ultima_accion
    
            if tiempo >= timedelta(minutes=timeout):
    
                print(
                    f"[MANTENIMIENTO] "
                    f"Viaje {viaje.id} "
                    f"requiere revisión."
                )
