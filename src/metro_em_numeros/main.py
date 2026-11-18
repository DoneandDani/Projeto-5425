
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from metro_em_numeros.config import obter_caminho_bd
from metro_em_numeros.database import initialize
from metro_em_numeros.web.indicadores import router

BASE_DIR = Path(__file__).resolve().parent

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize(app.state.db_path)
    yield

def create_app() -> FastAPI:
    
    app = FastAPI(title="Metro em Números", lifespan=lifespan)
    app.state.db_path = obter_caminho_bd()
    app.mount( "/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static",)
    app.include_router(router)
    return app