# Partilhado pelas diferentes rotas

from contextlib import contextmanager
from pathlib import Path

from fastapi import Request
from fastapi.templating import Jinja2Templates

from metro_em_numeros.database import connect

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@contextmanager
def open_connection(request: Request):
    """Uma ligação por pedido: abre-se aqui e fecha-se no fim (sebenta §10.2)."""
    conn = connect(request.app.state.db_path)
    try:
        yield conn
    finally:
        conn.close()


def integer_or_none(texto: str):
    """'3' -> 3; '' ou texto inválido -> None (o serviço trata como inválido)."""
    try:
        return int(texto)
    except (TypeError, ValueError):
        return None