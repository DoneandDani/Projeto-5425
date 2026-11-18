


from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from metro_em_numeros.database import connect
from metro_em_numeros.services.consulta_service import ConsultaService

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter(tags = ["indicadores"])

def build_service(conn) -> ConsultaService:
    return ConsultaService(conn)

@router.get("/")
def page_indicators(request: Request):
    
    conn = connect(request.app.state.db_path)
    
    try:
        contexto = build_service(conn).get_tables()
    finally:
        conn.close()
    
    return templates.TemplateResponse(
        request = request,
        name = "indicadores/lista.html",
        context=contexto,
    
    )