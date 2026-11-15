
import sqlite3
from pathlib import Path

CAMINHO_ESQUEMA = Path(__file__).resolve().parents[2] /"docs" / "schema.sql"

def connect(caminho: Path) -> sqlite3.Connection:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    conn =sqlite3.connect(caminho)
    conn.row_factory=sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def initialize(caminho: Path) -> None:
    esquema = CAMINHO_ESQUEMA.read_text(encoding="utf-8")
    conn=connect(caminho)
    try:
        conn.executescript(esquema)
    finally:
        conn.close()