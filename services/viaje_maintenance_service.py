from sqlalchemy.orm import Session

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
        pass

    @staticmethod
    def revisar_asignados(db: Session):
        pass

    @staticmethod
    def revisar_en_camino(db: Session):
        pass

    @staticmethod
    def revisar_llegados(db: Session):
        pass

    @staticmethod
    def revisar_en_curso(db: Session):
        pass
