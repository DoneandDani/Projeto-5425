

"""Prepara os dados para as páginas"""


from __future__ import annotations

import sqlite3

from metro_em_numeros.domain.series import Serie
from metro_em_numeros.repositories.importacao_repository import ImportacaoRepository
from metro_em_numeros.services.formatacao import format_value
from metro_em_numeros.services.series_service import SeriesService


def _for_table(serie: Serie) -> dict:
    return {
        "indicador": serie.titulo,
        "unidade": serie.unidade,
        "nota": serie.nota,
        "anos": serie.anos,
        "linhas": [
            {
                "nome": linha.nome,
                "e_total": linha.e_total,
                "valores": [format_value(v, serie.casas) for v in linha.valores],
            }
            for linha in serie.linhas
        ],
    }


class ConsultaService:
    def __init__(self, conn: sqlite3.Connection):
        self.series = SeriesService(conn)
        self.importacoes = ImportacaoRepository(conn)

    def get_tables(self) -> dict:
        """Uma tabela por indicador da fonte."""
        return self._context(derivadas=False)

    def get_analysis(self) -> dict:
        """Uma tabela por indicador calculado."""
        return self._context(derivadas=True)

    def _context(self, derivadas: bool) -> dict:
        catalogo = self.series.cataloge()
        ultima = self.importacoes.last()
        series = [s for s in catalogo.values() if s.derivada == derivadas]
        if not series or ultima is None:
            return {"tabelas": [], "periodo": None, "ultima_importacao": None}
        anos = series[0].anos
        return {
            "tabelas": [_for_table(s) for s in series],
            "periodo": f"{anos[0]}–{anos[-1]}",
            "ultima_importacao": ultima,
        }

    def options_graphs(self) -> list:
        """Séries disponíveis para o seletor da página de gráficos."""
        return [
            {"chave": s.chave, "titulo": s.titulo, "derivada": s.derivada}
            for s in self.series.catalog().values()
        ]