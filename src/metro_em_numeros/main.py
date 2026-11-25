
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from metro_em_numeros.config import obter_caminho_bd, obter_caminho_fatores
from metro_em_numeros.database import initialize
from metro_em_numeros.web.indicadores import router
from metro_em_numeros.web import  indicadores, linhas, modos

BASE_DIR = Path(__file__).resolve().parent

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize(app.state.db_path)
    yield

def create_app() -> FastAPI:
    
    app = FastAPI(title="Metro em Números", lifespan=lifespan)
    app.state.db_path = obter_caminho_bd()
    app.state.fatores_path = obter_caminho_fatores()
    app.mount(
        "/static",
        StaticFiles(directory=str(BASE_DIR / "static")),
        name="static",
    )
    for modulo in (indicadores, linhas, modos):
        app.include_router(modulo.router)
    return app