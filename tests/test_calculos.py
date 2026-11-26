import pytest

from metro_em_numeros.services.calculos import division, variation_percent


@pytest.mark.parametrize(
    "numerador, denominador, fator, esperado",
    [(50, 200, 100, 25.0), (1, 4, 1, 0.25), (0, 10, 100, 0.0),
     (None, 10, 1, None), (10, None, 1, None), (10, 0, 1, None)],
)
def test_razao(numerador, denominador, fator, esperado):
    assert division(numerador, denominador, fator) == esperado


@pytest.mark.parametrize(
    "anterior, atual, esperado",
    [(100, 110, 10.0), (100, 90, -10.0), (100, 100, 0.0),
     (0, 10, None), (None, 10, None), (10, None, None)],
)
def test_variacao_percentual(anterior, atual, esperado):
    assert variation_percent(anterior, atual) == esperado