

from __future__ import annotations

import sqlite3
from typing import List

from metro_em_numeros.domain.modelos import Indicador


class IndicadorRepository:
    
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def make_sure(self, indicador: Indicador) -> None:
        """Garante que o Indicador existe caso não esteja presente """
        self.conn.execute(
            "INSERT OR IGNORE INTO  indicador (nome, unidade) VALUES (?,?)", (indicador.nome, indicador.unidade),)

    def show_list(self) -> List[Indicador]:
        
        linhas= self.conn.execute( "SELECT nome, unidade FROM indicador ORDER BY id_indicador").fetchall()
        return [Indicador(nome=l["nome"], unidade=l["unidade"]) for l in linhas]
        