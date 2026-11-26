import pytest

from metro_em_numeros.domain.erros import InvalidImport
from metro_em_numeros.services.leitor_fatores import read_factors

CABECALHO = "modo,g_co2e_por_pkm,ano_referencia,ambito,fonte,url\n"


def escrever(tmp_path, linhas):
    caminho = tmp_path / "fatores.csv"
    caminho.write_text(CABECALHO + linhas, encoding="utf-8")
    return caminho


def test_le_fatores(tmp_path):
    caminho = escrever(tmp_path, "carro,100,2018,teste,fonte de teste,http://x\n"
                                 "comboio,10.5,2018,teste,fonte de teste,\n")
    fatores = read_factors(caminho)
    assert fatores["carro"].g_co2e_por_pkm == 100.0
    assert fatores["comboio"].g_co2e_por_pkm == 10.5


def test_valor_vazio_fica_por_preencher(tmp_path):
    fatores = read_factors(escrever(tmp_path, "carro,,2018,teste,fonte,\n"))
    assert not fatores["carro"].filled


def test_o_ficheiro_do_projeto_e_valido(csv_real):
    fatores = read_factors(csv_real.parent / "fatores_emissao.csv")
    assert {"carro", "comboio"} <= set(fatores)
    assert all(f.fonte and f.url for f in fatores.values())


@pytest.mark.parametrize(
    "linhas, mensagem",
    [("carro,abc,2018,t,f,\n", "inválido"),
     ("carro,-5,2018,t,f,\n", "positivo"),
     ("carro,10,xxxx,t,f,\n", "inválido"),
     ("carro,10,2018,t,,\n", "fonte"),
     ("carro,10,2018,t,f,\ncarro,11,2018,t,f,\n", "repetido")],
)
def test_erros(tmp_path, linhas, mensagem):
    with pytest.raises(InvalidImport, match=mensagem):
        read_factors(escrever(tmp_path, linhas))


def test_colunas_em_falta(tmp_path):
    caminho = tmp_path / "f.csv"
    caminho.write_text("modo,g_co2e_por_pkm\ncarro,10\n", encoding="utf-8")
    with pytest.raises(InvalidImport, match="Faltam colunas"):
        read_factors(caminho)