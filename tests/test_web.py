"""Testes das rotas. Ficam ignorados se o FastAPI/httpx não estiverem instalados."""
import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient  # noqa: E402

from metro_em_numeros.database import connect  # noqa: E402
from metro_em_numeros.main import create_app  # noqa: E402
from metro_em_numeros.services.importacao_service import ImportacaoService  # noqa: E402

CABECALHO_FATORES = "modo,g_co2e_por_pkm,ano_referencia,ambito,fonte,url\n"


@pytest.fixture
def cliente(tmp_path, monkeypatch):
    monkeypatch.setenv("METRO_DB_PATH", str(tmp_path / "web.db"))
    monkeypatch.setenv("METRO_FATORES_PATH", str(tmp_path / "fatores.csv"))
    with TestClient(create_app()) as c:  # o arranque cria as tabelas
        yield c


@pytest.fixture
def com_dados(cliente, tmp_path, csv_real):
    conn = connect(tmp_path / "web.db")
    try:
        ImportacaoService(conn).import_file(csv_real)
    finally:
        conn.close()


# ---- páginas de leitura ----
@pytest.mark.parametrize("url", ["/", "/analise", "/graficos"])
def test_paginas_sem_dados(cliente, url):
    resposta = cliente.get(url)
    assert resposta.status_code == 200
    assert "Ainda não existem dados" in resposta.text


def test_paginas_com_dados(cliente, com_dados):
    assert "35\u00a0069,0" in cliente.get("/").text
    assert "Taxa de ocupação" in cliente.get("/analise").text
    assert '<option value="ocupacao">' in cliente.get("/graficos").text


def test_api_de_series(cliente, com_dados):
    resposta = cliente.get("/api/series/passageiros")
    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["anos"][0] == 2016 and dados["series"][0]["nome"] == "Total (rede)"
    linha_g = next(s for s in dados["series"] if s["nome"] == "MP - G")
    assert None in linha_g["valores"]  # null no JSON
    assert cliente.get("/api/series/nao-existe").status_code == 404


def test_ficheiros_estaticos(cliente):
    assert cliente.get("/static/css/style.css").status_code == 200
    assert cliente.get("/static/js/graficos.js").status_code == 200


# ---- CRUD de modos ----
def test_crud_de_modos(cliente):
    resposta = cliente.post("/modos", data={"nome": "Metro", "descricao": ""},
                            follow_redirects=False)
    assert resposta.status_code == 303 and resposta.headers["location"] == "/modos"
    assert "Metro" in cliente.get("/modos").text

    repetido = cliente.post("/modos", data={"nome": "Metro", "descricao": ""})
    assert repetido.status_code == 422 and "Já existe" in repetido.text
    vazio = cliente.post("/modos", data={"nome": "  ", "descricao": ""})
    assert vazio.status_code == 422 and "obrigatório" in vazio.text

    assert cliente.get("/modos/1/editar").status_code == 200
    cliente.post("/modos/1", data={"nome": "Metro ligeiro", "descricao": "x"},
                 follow_redirects=False)
    assert "Metro ligeiro" in cliente.get("/modos").text

    cliente.post("/modos/1/eliminar", follow_redirects=False)
    assert "Metro ligeiro" not in cliente.get("/modos").text


def test_modo_inexistente_da_404(cliente):
    assert cliente.get("/modos/999/editar").status_code == 404
    assert cliente.post("/modos/999/eliminar").status_code == 404


# ---- CRUD de linhas ----
def test_crud_de_linhas(cliente):
    cliente.post("/modos", data={"nome": "Metro", "descricao": ""})
    resposta = cliente.post("/linhas", data={"codigo": "MP - A", "nome": "Linha A",
                                             "id_modo": "1"}, follow_redirects=False)
    assert resposta.status_code == 303
    assert "MP - A" in cliente.get("/linhas").text

    repetida = cliente.post("/linhas", data={"codigo": "MP - A", "nome": "X", "id_modo": "1"})
    assert repetida.status_code == 422 and "Já existe" in repetida.text
    sem_modo = cliente.post("/linhas", data={"codigo": "MP - B", "nome": "B", "id_modo": ""})
    assert sem_modo.status_code == 422 and "modo de transporte" in sem_modo.text

    cliente.post("/linhas/1", data={"nome": "Linha Azul", "id_modo": "1"},
                 follow_redirects=False)
    assert "Linha Azul" in cliente.get("/linhas").text
    assert cliente.get("/linhas/1/editar").status_code == 200

    cliente.post("/linhas/1/eliminar", follow_redirects=False)
    assert "MP - A" not in cliente.get("/linhas").text


def test_nao_elimina_modo_com_linhas(cliente):
    cliente.post("/modos", data={"nome": "Metro", "descricao": ""})
    cliente.post("/linhas", data={"codigo": "MP - A", "nome": "Linha A", "id_modo": "1"})
    resposta = cliente.post("/modos/1/eliminar")
    assert resposta.status_code == 422 and "linha(s) associada(s)" in resposta.text


def test_nao_elimina_linha_com_valores(cliente, com_dados):
    resposta = cliente.post("/linhas/1/eliminar")
    assert resposta.status_code == 422 and "valor(es) associado(s)" in resposta.text


def test_linha_inexistente_da_404(cliente):
    assert cliente.get("/linhas/999/editar").status_code == 404
    assert cliente.post("/linhas/999/eliminar").status_code == 404


# ---- impacto ----
def test_impacto_sem_ficheiro_de_fatores(cliente):
    resposta = cliente.get("/impacto")
    assert resposta.status_code == 200 and "Não foi encontrado" in resposta.text


def test_impacto_com_fatores_ficticios(cliente, com_dados, tmp_path):
    (tmp_path / "fatores.csv").write_text(
        CABECALHO_FATORES + "carro,100,2018,TESTE,Fonte de teste,\n"
                            "comboio,10,2018,TESTE,Fonte de teste,\n",
        encoding="utf-8",
    )
    resposta = cliente.get("/impacto?desvio=50")
    assert resposta.status_code == 200
    assert "Balanço de emissões por ano" in resposta.text
    assert "Fonte de teste" in resposta.text


def test_impacto_desvio_invalido(cliente):
    resposta = cliente.get("/impacto?desvio=150")
    assert resposta.status_code == 422 and "entre 0 e 100" in resposta.text


# ---- importar ----
def test_formulario_de_importar(cliente):
    assert "Importar dados" in cliente.get("/importar").text


def test_importar_csv_valido_e_repetido(cliente, csv_real):
    ficheiros = {"ficheiro": ("metro.csv", csv_real.read_bytes(), "text/csv")}
    primeira = cliente.post("/importar", files=ficheiros)
    assert primeira.status_code == 200 and "432 registos" in primeira.text
    assert "35\u00a0069,0" in cliente.get("/").text

    segunda = cliente.post("/importar", files=ficheiros)
    assert segunda.status_code == 200 and "já foi importado" in segunda.text


def test_importar_extensao_errada(cliente):
    resposta = cliente.post("/importar", files={"ficheiro": ("x.txt", b"abc", "text/plain")})
    assert resposta.status_code == 422 and ".csv" in resposta.text


def test_importar_csv_invalido_nao_grava(cliente):
    conteudo = b"Indicador (10^3),2024\r\nPassageiros,abc\r\n"
    resposta = cliente.post("/importar", files={"ficheiro": ("mau.csv", conteudo, "text/csv")})
    assert resposta.status_code == 422 and "valor inválido" in resposta.text
    assert "Ainda não existem dados" in cliente.get("/").text


def test_importar_ficheiro_demasiado_grande(cliente):
    conteudo = b"x" * (2 * 1024 * 1024 + 10)
    resposta = cliente.post("/importar", files={"ficheiro": ("grande.csv", conteudo, "text/csv")})
    assert resposta.status_code == 422 and "2 MB" in resposta.text