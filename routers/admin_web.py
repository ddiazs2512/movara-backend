from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/admin",
    tags=["Movara Control Center"]
)

templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="dashboard/index.html",
        context={
            "page_title": "Dashboard"
        }
    )
