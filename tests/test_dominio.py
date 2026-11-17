
import math
import pytest

from metro_em_numeros.domain.erros import InvalidData
from metro_em_numeros.domain.modelos import Importacao, Indicador, Linha, ValorIndicador


HASH = "a" * 64


def test_linha_a_partir_do_codigo():
    linha = Linha.from_the_code("MP - A")
    assert linha.codigo == "MP - A"
    assert linha.nome == "Linha A"

@pytest.mark.parametrize("codigo", ["MP - H", "A", "", "MP-A", "mp - a", "MP - AB"])
def test_linha_invalida(codigo):
    with pytest.raises(InvalidData):
        Linha.from_the_code(codigo)


def test_linha_sem_nome_e_invalida():
    with pytest.raises(InvalidData):
        Linha(codigo="MP - A", nome="  ")

def test_indicador_conhecido_tem_unidade():
    assert Indicador.known("Passageiros").unidade == "10^3 passageiros"

def test_indicador_desconhecido():
    with pytest.raises(InvalidData, match="desconhecido"):
        Indicador.known("Bananas")

def test_valor_total_e_chave():
    valor = ValorIndicador(Indicador.known("Comboios"), None, 2024, 373.2)
    assert valor.e_total
    assert valor.key == ("Comboios", None, 2024)


def test_valor_de_linha_e_chave():
    valor = ValorIndicador( Indicador.known("Comboios"), Linha.from_the_code("MP - B"), 2020, 41.7)
    assert not valor.e_total
    assert valor.key == ("Comboios", "MP - B", 2020)


def test_sem_dados_e_diferente_de_zero():
    indicador = Indicador.known("Passageiros")
    assert ValorIndicador(indicador, None, 2024, None).valor is None
    assert ValorIndicador(indicador, None, 2024, 0.0).valor == 0.0


def test_ano_fora_do_intervalo():
    with pytest.raises(InvalidData, match="fora do intervalo"):
        ValorIndicador(Indicador.known("Comboios"), None, 1800, 1.0)


@pytest.mark.parametrize("valor", [math.nan, math.inf])
def test_valor_nao_finito(valor):
    with pytest.raises(InvalidData):
        ValorIndicador(Indicador.known("Comboios"), None, 2024, valor)


def test_importacao_valida():
    importacao = Importacao(None, "a.csv", HASH, "fonte", 10)
    assert importacao.id is None


@pytest.mark.parametrize(
    "nome, hash_sha256, fonte, registos",
    [
        ("", HASH, "fonte", 1),
        ("a.csv", "curto", "fonte", 1),
        ("a.csv", HASH, " ", 1),
        ("a.csv", HASH, "fonte", -1),
    ],
)
def test_importacao_invalida(nome, hash_sha256, fonte, registos):
    with pytest.raises(InvalidData):
        Importacao(None, nome, hash_sha256, fonte, registos)
