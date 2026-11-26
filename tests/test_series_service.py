import pytest

from metro_em_numeros.services.series_service import SeriesService, serie_for_json


def valores_da_linha(serie, nome):
    linha = next(l for l in serie.linhas if l.nome == nome)
    return dict(zip(serie.anos, linha.valores))


def test_sem_dados_o_catalogo_e_vazio(conn):
    assert SeriesService(conn).cataloge() == {}


def test_ordem_do_catalogo(conn_com_dados):
    catalogo = SeriesService(conn_com_dados).cataloge()
    assert list(catalogo) == [
        "comboios", "comboios-km", "investimento", "lugares-km",
        "passageiros", "passageiros-km",
        "ocupacao", "distancia-media", "passageiros-por-comboio-km",
        "variacao-passageiros", "quota-passageiros",
    ]
    assert [s.derivada for s in catalogo.values()].count(True) == 5


def test_serie_base(conn_com_dados):
    serie = SeriesService(conn_com_dados).cataloge()["passageiros"]
    assert serie.unidade == "10³ passageiros"
    assert serie.anos == list(range(2016, 2025))
    assert serie.linhas[0].e_total and serie.linhas[0].nome == "Total (rede)"
    assert valores_da_linha(serie, "Total (rede)")[2024] == 89780.4
    assert valores_da_linha(serie, "MP - D")[2024] == 35069.0
    assert valores_da_linha(serie, "MP - G")[2024] is None


def test_ocupacao_do_total(conn_com_dados):
    serie = SeriesService(conn_com_dados).cataloge()["ocupacao"]
    total = valores_da_linha(serie, "Total (rede)")
    assert total[2024] == pytest.approx(477564.1 / 2104147.4 * 100, abs=0.01)
    assert 0 < total[2024] < 100


def test_nenhuma_ocupacao_acima_de_100(conn_com_dados):
    serie = SeriesService(conn_com_dados).cataloge()["ocupacao"]
    for linha in serie.linhas:
        assert all(v is None or v <= 100 for v in linha.valores), linha.nome


def test_distancia_media_do_total(conn_com_dados):
    serie = SeriesService(conn_com_dados).cataloge()["distancia-media"]
    assert valores_da_linha(serie, "Total (rede)")[2024] == pytest.approx(
        477564.1 / 89780.4, abs=0.01
    )


def test_passageiros_por_comboio_km(conn_com_dados):
    serie = SeriesService(conn_com_dados).cataloge()["passageiros-por-comboio-km"]
    assert valores_da_linha(serie, "Total (rede)")[2024] == pytest.approx(
        89780.4 / 5513.1, abs=0.01
    )


def test_variacao_anual(conn_com_dados):
    serie = SeriesService(conn_com_dados).cataloge()["variacao-passageiros"]
    total = valores_da_linha(serie, "Total (rede)")
    assert total[2016] is None  # sem ano anterior
    assert total[2017] == pytest.approx((60593.2 - 57999.9) / 57999.9 * 100, abs=0.01)


def test_quota_das_linhas_soma_100(conn_com_dados):
    serie = SeriesService(conn_com_dados).cataloge()["quota-passageiros"]
    assert all(not l.e_total for l in serie.linhas)  # sem linha do total
    for indice, ano in enumerate(serie.anos):
        soma = sum(l.valores[indice] or 0 for l in serie.linhas)
        assert soma == pytest.approx(100, abs=0.1), ano


def test_linha_sem_dados_nao_gera_valores_derivados(conn_com_dados):
    serie = SeriesService(conn_com_dados).cataloge()["ocupacao"]
    assert valores_da_linha(serie, "MP - G")[2024] is None


def test_serie_para_json(conn_com_dados):
    serie = SeriesService(conn_com_dados).catalogo()["passageiros"]
    dados = serie_for_json(serie)
    assert dados["chave"] == "passageiros"
    assert dados["anos"][0] == 2016
    assert dados["series"][0]["nome"] == "Total (rede)"
    linha_g = next(s for s in dados["series"] if s["nome"] == "MP - G")
    assert None in linha_g["valores"]