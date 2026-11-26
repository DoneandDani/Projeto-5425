"""Os fatores usados aqui são números inventados, só para testar a conta."""
import pytest

from metro_em_numeros.domain.erros import InvalidData
from metro_em_numeros.services.formatacao import format_value
from metro_em_numeros.services.impacto_service import ImpactoService

CABECALHO = "modo,g_co2e_por_pkm,ano_referencia,ambito,fonte,url\n"


@pytest.fixture
def fatores_ficticios(tmp_path):
    caminho = tmp_path / "fatores.csv"
    caminho.write_text(
        CABECALHO + "carro,100,2018,TESTE,fonte de teste,\n"
                    "comboio,10,2018,TESTE,fonte de teste,\n",
        encoding="utf-8",
    )
    return caminho


def linha_do_ano(resultado, ano):
    return next(l for l in resultado["linhas"] if l["ano"] == ano)


def test_balanco_com_fatores_ficticios(conn_com_dados, fatores_ficticios):
    resultado = ImpactoService(conn_com_dados, fatores_ficticios).estimate(100)
    assert resultado["disponivel"]
    pkm = 477564.1 * 1000  # passageiros-km do total, 2024
    metro_t = pkm * 10 / 1e6
    alternativa_t = pkm * 100 / 1e6
    linha = linha_do_ano(resultado, 2024)
    assert linha["metro_t"] == format_value(metro_t, 0)
    assert linha["alternativa_t"] == format_value(alternativa_t, 0)
    assert linha["balanco_t"] == format_value(alternativa_t - metro_t, 0)
    assert [l["ano"] for l in resultado["linhas"]] == list(range(2016, 2025))


def test_com_desvio_zero_o_balanco_e_negativo(conn_com_dados, fatores_ficticios):
    resultado = ImpactoService(conn_com_dados, fatores_ficticios).estimate(0)
    assert linha_do_ano(resultado, 2024)["alternativa_t"] == "0"
    assert linha_do_ano(resultado, 2024)["balanco_t"].startswith("-")


@pytest.mark.parametrize("desvio", [-1, 101, float("nan")])
def test_desvio_invalido(conn_com_dados, fatores_ficticios, desvio):
    with pytest.raises(InvalidData):
        ImpactoService(conn_com_dados, fatores_ficticios).estimate(desvio)


def test_sem_ficheiro_de_fatores(conn_com_dados, tmp_path):
    resultado = ImpactoService(conn_com_dados, tmp_path / "nao_existe.csv").estimate()
    assert not resultado["disponivel"]
    assert "Não foi encontrado" in resultado["mensagens"][0]


def test_fatores_por_preencher_nao_calcula(conn_com_dados, csv_real):
    ficheiro = csv_real.parent / "fatores_emissao.csv"  # o do projeto, sem valores
    resultado = ImpactoService(conn_com_dados, ficheiro).estimate()
    assert not resultado["disponivel"]
    assert "carro" in resultado["mensagens"][0] and "comboio" in resultado["mensagens"][0]
    assert resultado["linhas"] == []


def test_sem_dados_importados(conn, fatores_ficticios):
    resultado = ImpactoService(conn, fatores_ficticios).estimate()
    assert not resultado["disponivel"]
    assert "Passageiros-Km" in resultado["mensagens"][0]