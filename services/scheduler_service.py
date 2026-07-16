import threading
import time
import logging

from database import SessionLocal
from services.viaje_maintenance_service import ViajeMaintenanceService

logger = logging.getLogger(__name__)

_running = False


def _worker():

    global _running

    while _running:

        db = SessionLocal()

        try:

            ViajeMaintenanceService.ejecutar(db)

        except Exception as e:

            logger.exception(
                f"[MANTENIMIENTO] Error: {e}"
            )

        finally:

            db.close()

        time.sleep(60)


def iniciar_scheduler():

    global _running

    if _running:
        return

    _running = True

    hilo = threading.Thread(
        target=_worker,
        daemon=True
    )

    hilo.start()

    logger.info(
        "[MANTENIMIENTO] Scheduler iniciado."
    )
