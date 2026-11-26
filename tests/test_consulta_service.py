"""Dados preparados para a página e renderização do template."""
from pathlib import Path

import pytest
from jinja2 import Environment, FileSystemLoader

import metro_em_numeros
from metro_em_numeros.database import connect
from metro_em_numeros.services.consulta_service import ConsultaService
from metro_em_numeros.services.formatacao import format_value
from metro_em_numeros.services.importacao_service import ImportacaoService

TEMPLATES = Path(metro_em_numeros.__file__).resolve().parent / "templates"


def renderizar(contexto):
    """Renderiza o template sem FastAPI (url_for é simulado)."""
    ambiente = Environment(loader=FileSystemLoader(str(TEMPLATES)), autoescape=True)
    ambiente.globals["url_for"] = lambda nome, path: "/static" + path
    return ambiente.get_template("indicadores/lista.html").render(**contexto)


def test_sem_dados(conn):
    contexto = ConsultaService(conn).get_tables()
    assert contexto["tabelas"] == []
    assert "Ainda não existem dados importados" in renderizar(contexto)


def test_com_dados(conn, csv_real):
    ImportacaoService(conn).import_file(csv_real)
    contexto = ConsultaService(conn).get_tables()
    assert contexto["periodo"] == "2016–2024"
    assert [t["indicador"] for t in contexto["tabelas"]] == [
        "Comboios", "Comboios-Km", "Investimento",
        "Lugares-Km", "Passageiros", "Passageiros-Km",
    ]
    html = renderizar(contexto)
    assert "35\u00a0069,0" in html      # Passageiros, MP - D, 2024
    assert "10^3 passageiros" in html
    assert "Total (rede)" in html
    assert "—" in html                  # linha G sem dados


def test_os_dados_persistem_apos_reabrir(path_db, csv_real):
    with_conn = connect(path_db)
    try:
        ImportacaoService(with_conn).import_file(csv_real)
    finally:
        with_conn.close()
    # "reiniciar": nova ligação, como num novo arranque da aplicação
    nova = connect(path_db)
    try:
        assert len(ConsultaService(nova).get_tables()["tabelas"]) == 6
    finally:
        nova.close()


@pytest.mark.parametrize(
    "valor, esperado",
    [(5274.2, "5\u00a0274,2"), (0.0, "0,0"), (None, "—"), (1594742.1, "1\u00a0594\u00a0742,1")],
)
def test_formatar_valor(valor, esperado):
    assert format_value(valor) == esperado


def test_formatar_com_casas_decimais():
    assert format_value(1234.5678, 0) == "1\u00a0235"
    assert format_value(1234.5678, 2) == "1\u00a0234,57"
    assert format_value(-1234.5, 1) == "-1\u00a0234,5"


def test_analise_so_tem_series_derivadas(conn_with_data):
    contexto = ConsultaService(conn_with_data).get_analysis()
    titulos = [t["indicador"] for t in contexto["tabelas"]]
    assert "Taxa de ocupação" in titulos
    assert "Passageiros" not in titulos
    html = renderizar_analise(contexto)
    assert "Taxa de ocupação" in html


def test_opcoes_de_graficos(conn_with_data):
    opcoes = ConsultaService(conn_with_data).options_graphs()
    chaves = [o["chave"] for o in opcoes]
    assert chaves[:6] == ["comboios", "comboios-km", "investimento",
                          "lugares-km", "passageiros", "passageiros-km"]
    assert "ocupacao" in chaves
    assert [o["derivada"] for o in opcoes].count(True) == 5


def renderizar_analise(contexto):
    ambiente = Environment(loader=FileSystemLoader(str(TEMPLATES)), autoescape=True)
    ambiente.globals["url_for"] = lambda nome, path: "/static" + path
    return ambiente.get_template("analise/lista.html").render(**contexto)