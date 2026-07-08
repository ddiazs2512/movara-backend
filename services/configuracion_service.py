from sqlalchemy.orm import Session

from models import Configuracion


class ConfiguracionService:

    @staticmethod
    def obtener(
        db: Session,
        grupo: str,
        clave: str
    ):

        return (
            db.query(Configuracion)
            .filter(
                Configuracion.grupo == grupo,
                Configuracion.clave == clave
            )
            .first()
        )

    @staticmethod
    def obtener_string(
        db: Session,
        grupo: str,
        clave: str,
        default: str = ""
    ) -> str:

        config = ConfiguracionService.obtener(
            db,
            grupo,
            clave
        )

        if config is None:
            return default

        return config.valor

    @staticmethod
    def obtener_int(
        db: Session,
        grupo: str,
        clave: str,
        default: int = 0
    ) -> int:

        config = ConfiguracionService.obtener(
            db,
            grupo,
            clave
        )

        if config is None:
            return default

        return int(config.valor)

    @staticmethod
    def obtener_float(
        db: Session,
        grupo: str,
        clave: str,
        default: float = 0.0
    ) -> float:

        config = ConfiguracionService.obtener(
            db,
            grupo,
            clave
        )

        if config is None:
            return default

        return float(config.valor)

    @staticmethod
    def obtener_bool(
        db: Session,
        grupo: str,
        clave: str,
        default: bool = False
    ) -> bool:

        config = ConfiguracionService.obtener(
            db,
            grupo,
            clave
        )

        if config is None:
            return default

        return config.valor.lower() == "true"
