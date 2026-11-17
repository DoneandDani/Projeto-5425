
from pathlib import Path

import pytest

from metro_em_numeros.database import initialize, connect

RAIZ = Path(__file__).resolve().parent.parent

CSV_PEQUENO = (
    "Indicador (10^3),2023,2024,% do Total\r\n"
    "Passageiros,\"79,140.70\",\"89,780.40\",100.00\r\n"
    "MP - A,\"12,493.70\",\"13,981.40\",15.60\r\n"
    "MP - G,,,\r\n"
)

@pytest.fixture
def csv_real():
    return RAIZ / "data" / "data_2016_2024.csv"

@pytest.fixture
def write_csv(tmp_path):
    """Devolve uma função que escreve um CSV de teste e devolve o caminho."""

    def _write(conteudo, nome="amostra.csv"):
        caminho =tmp_path / nome
        caminho.write_text(conteudo, encoding="utf-8", newline="")
        return caminho
    return _write

@pytest.fixture
def text_csv_small():
    return CSV_PEQUENO

@pytest.fixture
def csv_small(write_csv):
    return write_csv(CSV_PEQUENO)

@pytest.fixture
def path_db(tmp_path):
    caminho = tmp_path / "teste.db"
    initialize(caminho)
    return caminho

@pytest.fixture
def conn(path_db):

    conn =connect(path_db)
    
    try:
        yield conn
    finally:
        conn.close()


@pytest.fixture
def count_lines(conn):
    """Devolve uma função que conta as linhas de uma dada tabela."""

    def _count_lines(tabela):
        return conn.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]
    return _count_lines




