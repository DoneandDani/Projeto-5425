import math

import pytest

from metro_em_numeros.domain.erros import InvalidData
from metro_em_numeros.domain.impacto import FatorEmissao
from metro_em_numeros.domain.modelos import (
    Importacao,
    Indicador,
    Linha,
    ModoTransporte,
    ValorIndicador,
)

HASH = "a" * 64


# ---- Linha ----
def test_linha_normaliza_codigo_e_nome():
    linha = Linha(codigo=" MP - A ", nome="  Linha   A ")
    assert linha.codigo == "MP - A"
    assert linha.nome == "Linha A"


@pytest.mark.parametrize(
    "codigo, nome",
    [("", "Linha A"), ("   ", "Linha A"), ("x" * 21, "Linha A"),
     ("A", ""), ("A", "  "), ("A", "x" * 101)],
)
def test_linha_invalida(codigo, nome):
    with pytest.raises(InvalidData):
        Linha(codigo=codigo, nome=nome)


# ---- ModoTransporte ----
def test_modo_normaliza_e_descricao_vazia_vira_none():
    modo = ModoTransporte(nome="  Metro   ligeiro ", descricao="   ")
    assert modo.nome == "Metro ligeiro"
    assert modo.descricao is None


@pytest.mark.parametrize(
    "nome, descricao",
    [("", None), ("  ", None), ("x" * 101, None), ("Metro", "x" * 256)],
)
def test_modo_invalido(nome, descricao):
    with pytest.raises(InvalidData):
        ModoTransporte(nome=nome, descricao=descricao)


# ---- Indicador ----
def test_indicador_conhecido_tem_unidade():
    assert Indicador.known("Passageiros").unidade == "10³ passageiros"


def test_indicador_desconhecido():
    with pytest.raises(InvalidData, match="desconhecido"):
        Indicador.known("Bananas")


# ---- ValorIndicador ----
def test_valor_total_e_chave():
    valor = ValorIndicador(Indicador.known("Comboios"), None, 2024, 373.2)
    assert valor.e_total
    assert valor.key == ("Comboios", None, 2024)


def test_valor_de_linha_e_chave():
    valor = ValorIndicador(
        Indicador.known("Comboios"), Linha(codigo="MP - B", nome="Linha B"), 2020, 41.7
    )
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


# ---- Importacao ----
def test_importacao_valida():
    assert Importacao(None, "a.csv", HASH, "fonte", 10).id is None


@pytest.mark.parametrize(
    "nome, hash_sha256, fonte, registos",
    [("", HASH, "fonte", 1), ("a.csv", "curto", "fonte", 1),
     ("a.csv", HASH, " ", 1), ("a.csv", HASH, "fonte", -1)],
)
def test_importacao_invalida(nome, hash_sha256, fonte, registos):
    with pytest.raises(InvalidData):
        Importacao(None, nome, hash_sha256, fonte, registos)


# ---- FatorEmissao ----
def test_fator_por_preencher_e_valido():
    fator = FatorEmissao("carro", None, 2018, "EU-27", "fonte", "")
    assert not fator.filled


@pytest.mark.parametrize("valor", [0, -1, math.nan, math.inf])
def test_fator_invalido(valor):
    with pytest.raises(InvalidData):
        FatorEmissao("carro", valor, 2018, "EU-27", "fonte", "")