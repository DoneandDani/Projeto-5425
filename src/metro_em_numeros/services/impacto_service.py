
"""Estimativa simples do balanço de emissões (CO2e) do metro."""
from __future__ import annotations

import math
import sqlite3
from pathlib import Path

from metro_em_numeros.domain.erros import InvalidData
from metro_em_numeros.services.formatacao import format_value
from metro_em_numeros.services.leitor_fatores import read_factors
from metro_em_numeros.services.series_service import SeriesService

MODO_ALTERNATIVA = "carro"
MODO_METRO = "comboio"  # média ferroviária usada como aproximação do metro


class ImpactoService:
    def __init__(self, conn: sqlite3.Connection, caminho_fatores):
        self.series = SeriesService(conn)
        self.caminho_fatores = Path(caminho_fatores)

    def estimate(self, desvio_percentual: float = 100.0) -> dict:
        """Balanço por ano, para o cenário em que `desvio_percentual` % dos
        passageiros-km do metro seriam feitos de carro.

        Balanço = emissões da alternativa - emissões do metro (toneladas CO2e).
        Os restantes passageiros-km são assumidos sem emissões alternativas.
        """
        if math.isnan(desvio_percentual) or not (0 <= desvio_percentual <= 100):
            raise InvalidData("A percentagem tem de estar entre 0 e 100.")

        resultado = {
            "disponivel": False, "desvio": desvio_percentual,
            "mensagens": [], "fatores": [], "linhas": [], "total_balanco": None,
        }
        try:
            fatores = read_factors(self.caminho_fatores)
        except FileNotFoundError:
            resultado["mensagens"] = [
                f"Não foi encontrado o ficheiro de fatores de emissão: {self.caminho_fatores}"
            ]
            return resultado

        resultado["fatores"] = list(fatores.values())
        em_falta = [
            modo for modo in (MODO_ALTERNATIVA, MODO_METRO)
            if modo not in fatores or not fatores[modo].filled
        ]
        if em_falta:
            resultado["mensagens"] = [
                "Falta preencher o fator de emissão (g CO2e por passageiro-km) de: "
                + ", ".join(em_falta) + "."
            ]
            return resultado

        serie = self.series.cataloge().get("passageiros-km")
        total = None if serie is None else next((l for l in serie.linhas if l.e_total), None)
        if total is None:
            resultado["mensagens"] = ["Ainda não existem dados de Passageiros-Km."]
            return resultado

        f_carro = fatores[MODO_ALTERNATIVA].g_co2e_por_pkm
        f_metro = fatores[MODO_METRO].g_co2e_por_pkm
        linhas, balanco_total = [], 0.0
        for ano, milhares_pkm in zip(serie.anos, total.valores):
            if milhares_pkm is None:
                continue
            pkm = milhares_pkm * 1000
            metro_t = pkm * f_metro / 1e6
            alternativa_t = pkm * (desvio_percentual / 100) * f_carro / 1e6
            balanco = alternativa_t - metro_t
            balanco_total += balanco
            linhas.append({
                "ano": ano,
                "milhoes_pkm": format_value(pkm / 1e6, 1),
                "metro_t": format_value(metro_t, 0),
                "alternativa_t": format_value(alternativa_t, 0),
                "balanco_t": format_value(balanco, 0),
            })

        resultado.update(
            disponivel=True, linhas=linhas,
            total_balanco=format_value(balanco_total, 0),
        )
        return resultado