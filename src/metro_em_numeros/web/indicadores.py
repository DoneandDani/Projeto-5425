


from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from metro_em_numeros.database import connect
from metro_em_numeros.services.consulta_service import ConsultaService
from metro_em_numeros.web.comum import open_connection, templates

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter(tags = ["indicadores"])

def build_service(conn) -> ConsultaService:
    return ConsultaService(conn)

@router.get("/")
def pagina_indicadores(request: Request):
    with open_connection(request) as conn:
        contexto = ConsultaService(conn).get_tables()
    return templates.TemplateResponse(
        request=request, name="indicadores/lista.html", context=contexto
    )