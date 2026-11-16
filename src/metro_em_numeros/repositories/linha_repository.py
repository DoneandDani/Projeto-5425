

from __future__ import annotations


import sqlite3
from typing import List

from metro_em_numeros.domain.modelos import Linha

MODO_PADRAO = "Metro"


class LinhaRepository:
    def __innit__(self,conn:sqlite3.Connection):
        self.conn =conn

    def make_sure(self, linha:Linha, modo:str =MODO_PADRAO) -> None:
        
        """Garante que o modo e a linha existem, se já não tiverem presentes."""
        
        self.conn.execute( "INSERT OR IGNORE INTO modo_transporte (nome) VALUES (?)", 
                          (modo,),)

        self.conn.execute(
            """INSERT OR IGNORE INTO linha (id_modo, codigo, nome)
            VALUES (
                (SELECT id_modo FROM modo_transporte WHERE nome = ?),
                ?, ?
            )
            
            """,
            (modo, linha.codigo, linha.nome),
        )

    def show_list(self) ->List[Linha]:
        linhas = self.conn.execute ( "SELECT codigo, nome FROM linha ORDER BY codigo").fetchall()
        return [Linha(codigo=l["codigo"], nome=l["nome"]) for l in linhas]

