from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy import text

from database import get_db
from models import Usuario, Viaje

router = APIRouter(
    prefix="/admin",
    tags=["Movara Control Center"]
)

templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db)
):

    # ===========================
    # Usuarios
    # ===========================

    total_usuarios = db.query(func.count(Usuario.id)).scalar() or 0

    # ===========================
    # Clientes
    # ===========================

    clientes_registrados = db.query(Usuario).filter(
        Usuario.rol == "cliente"
    ).count()

    # ===========================
    # Conductores
    # ===========================

    conductores_online = db.query(Usuario).filter(
        Usuario.rol == "conductor"
    ).count()

    # ===========================
    # Viajes Activos
    # ===========================

    viajes_activos = db.query(Viaje).filter(
        Viaje.estado.in_([
            "oferta",
            "asignado",
            "en_camino",
            "llegado",
            "en_curso"
        ])
    ).count()

    # ===========================
    # Entregas
    # ===========================
    # (Temporalmente usa 0 hasta implementar
    # el módulo de entregas)

    entregas_activas = 0

    # ===========================
    # Estado PostgreSQL
    # ===========================
    
    try:
        db.execute(text("SELECT 1"))
        postgres_estado = "✅ Operativo"
    except Exception:
        postgres_estado = "❌ Sin conexión"

    return templates.TemplateResponse(
        request=request,
        name="dashboard/index.html",
        context={
            "page_title": "Dashboard",
            "usuarios": total_usuarios,
            "clientes": clientes_registrados,
            "conductores": conductores_registrados,
            "viajes": viajes_activos,
            "entregas": entregas_activas,
            "postgres_estado": postgres_estado
        }
    )
