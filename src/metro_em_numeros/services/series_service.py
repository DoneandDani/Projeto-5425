"""Séries por indicador (base e derivadas), prontas para tabelas e gráficos."""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Callable, Dict, Optional

from metro_em_numeros.domain.series import LinhaSerie, Serie
from metro_em_numeros.repositories.valor_repository import ValorRepository
from metro_em_numeros.services.calculos import division, variation_percent

NOME_TOTAL = "Total (rede)"

# dados[(indicador, codigo_da_linha_ou_None, ano)] -> valor
Dados = Dict[tuple, Optional[float]]


def _occupancy(d: Dados, linha, ano) -> Optional[float]:
    return division(d.get(("Passageiros-Km", linha, ano)), d.get(("Lugares-Km", linha, ano)), 100)


def _average_distance(d: Dados, linha, ano) -> Optional[float]:
    return division(d.get(("Passageiros-Km", linha, ano)), d.get(("Passageiros", linha, ano)))


def _passangers_per_train_km(d: Dados, linha, ano) -> Optional[float]:
    return division(d.get(("Passageiros", linha, ano)), d.get(("Comboios-Km", linha, ano)))


def _variation_passangers(d: Dados, linha, ano) -> Optional[float]:
    return variation_percent(
        d.get(("Passageiros", linha, ano - 1)), d.get(("Passageiros", linha, ano))
    )


def _quota_passagers(d: Dados, linha, ano) -> Optional[float]:
    if linha is None:
        return None
    return division(d.get(("Passageiros", linha, ano)), d.get(("Passageiros", None, ano)), 100)


@dataclass(frozen=True)
class _Derivada:
    chave: str
    titulo: str
    unidade: str
    calcular: Callable
    incluir_total: bool = True
    nota: str = ""


DERIVADAS = [
    _Derivada(
        "ocupacao", "Taxa de ocupação", "%", _occupancy,
        nota="Passageiros-km a dividir por lugares-km. Estima a parte da "
             "capacidade oferecida que foi utilizada.",
    ),
    _Derivada(
        "distancia-media", "Distância média por passageiro", "km", _average_distance,
        nota="Passageiros-km a dividir por passageiros. Os valores por linha "
             "de 2016 parecem inconsistentes na fonte.",
    ),
    _Derivada(
        "passageiros-por-comboio-km", "Passageiros por comboio-km", "passageiros/km",
        _passangers_per_train_km,
        nota="Passageiros a dividir por comboios-km.",
    ),
    _Derivada(
        "variacao-passageiros", "Variação anual de passageiros", "%", _variation_passangers,
        nota="Variação face ao ano anterior. O primeiro ano não tem valor.",
    ),
    _Derivada(
        "quota-passageiros", "Quota das linhas nos passageiros", "%", _quota_passagers,
        incluir_total=False,
        nota="Passageiros de cada linha a dividir pelo total da rede.",
    ),
]


def _chave(nome: str) -> str:
    return nome.lower()


class SeriesService:
    def __init__(self, conn: sqlite3.Connection):
        self.valores = ValorRepository(conn)

    def cataloge(self) -> Dict[str, Serie]:
        """Séries base (uma por indicador) e derivadas, por esta ordem."""
        valores = self.valores.listing()
        if not valores:
            return {}

        dados: Dados = {v.key: v.valor for v in valores}
        anos = sorted({v.ano for v in valores})
        linhas = list(dict.fromkeys(v.linha.codigo if v.linha else None for v in valores))
        indicadores = list(dict.fromkeys(v.indicador for v in valores))

        catalogo: Dict[str, Serie] = {}
        for indicador in indicadores:
            chave = _chave(indicador.nome)
            catalogo[chave] = self._build(
                chave, indicador.nome, indicador.unidade, anos, linhas,
                lambda linha, ano, nome=indicador.nome: dados.get((nome, linha, ano)),
                derivada=False, incluir_total=True, nota="",
            )
        for d in DERIVADAS:
            catalogo[d.chave] = self._build(
                d.chave, d.titulo, d.unidade, anos, linhas,
                lambda linha, ano, calc=d.calcular: calc(dados, linha, ano),
                derivada=True, incluir_total=d.incluir_total, nota=d.nota,
            )
        return catalogo

    @staticmethod
    def _build(chave, titulo, unidade, anos, linhas, valor_de, derivada, incluir_total, nota):
        series = [
            LinhaSerie(
                nome=NOME_TOTAL if linha is None else linha,
                e_total=linha is None,
                valores=[valor_de(linha, ano) for ano in anos],
            )
            for linha in linhas
            if incluir_total or linha is not None
        ]
        return Serie(
            chave=chave, titulo=titulo, unidade=unidade, anos=anos,
            linhas=series, derivada=derivada, nota=nota,
        )


def serie_for_json(serie: Serie) -> dict:
    """Estrutura que o JavaScript dos gráficos recebe (None vira null)."""
    return {
        "chave": serie.chave,
        "titulo": serie.titulo,
        "unidade": serie.unidade,
        "derivada": serie.derivada,
        "nota": serie.nota,
        "anos": serie.anos,
        "series": [{"nome": l.nome, "valores": l.valores} for l in serie.linhas],
    }