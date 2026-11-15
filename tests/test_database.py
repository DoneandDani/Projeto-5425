
import sqlite3
import pytest

from metro_em_numeros.database import initialize, connect




@pytest.fixture
def caminho(tmp_path):
    caminho = tmp_path / "teste.db"
    initialize(caminho)
    return caminho


@pytest.fixture
def conn(caminho):
    conn = connect(caminho)
    try:
        yield conn
    finally:
        conn.close()


def preparar_base(conn):
    """Cria importação e indicador para os testes de valor_indicador."""
    with conn:
        conn.execute(
            "INSERT INTO importacao (nome_ficheiro, hash_sha256, fonte, num_registos) "
            "VALUES ('teste.csv', 'abc', 'teste', 0)"
        )
        conn.execute(
            "INSERT INTO indicador (nome, unidade) VALUES ('Passageiros', '10³ passageiros')"
        )


def test_cria_as_cinco_tabelas(conn):
    linhas = conn.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
    ).fetchall()
    assert {linha["name"] for linha in linhas} == {
        "modo_transporte", "linha", "indicador", "importacao", "valor_indicador",
    }


def test_inicializar_duas_vezes_nao_apaga_dados(caminho, conn):
    with conn:
        conn.execute("INSERT INTO modo_transporte (nome) VALUES ('Metro')")
    initialize(caminho)
    total = conn.execute("SELECT COUNT(*) FROM modo_transporte").fetchone()[0]
    assert total == 1


def test_chaves_estrangeiras_estao_ativas(conn):
    with pytest.raises(sqlite3.IntegrityError):
        with conn:
            conn.execute(
                "INSERT INTO linha (id_modo, codigo, nome) VALUES (999, 'MP - A', 'Linha A')"
            )


def test_impede_dois_totais_para_o_mesmo_indicador_e_ano(conn):
    preparar_base(conn)
    sql = (
        "INSERT INTO valor_indicador (id_importacao, id_indicador, id_linha, ano, valor) "
        "VALUES (1, 1, NULL, 2024, 1.0)"
    )
    with conn:
        conn.execute(sql)
    with pytest.raises(sqlite3.IntegrityError):
        with conn:
            conn.execute(sql)


def test_aceita_valor_nulo_e_rejeita_ano_invalido(conn):
    preparar_base(conn)
    with conn:
        conn.execute(
            "INSERT INTO valor_indicador (id_importacao, id_indicador, id_linha, ano, valor) "
            "VALUES (1, 1, NULL, 2024, NULL)"
        )
    with pytest.raises(sqlite3.IntegrityError):
        with conn:
            conn.execute(
                "INSERT INTO valor_indicador (id_importacao, id_indicador, id_linha, ano, valor) "
                "VALUES (1, 1, NULL, 1800, 1.0)"
            )