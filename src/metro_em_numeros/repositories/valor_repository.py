

from __future__ import annotations

import sqlite3
from typing import Iterable, List, Optional, Set, Tuple

from metro_em_numeros.domain.modelos import Indicador, Linha, ValorIndicador


class ValorRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def existing_keys(self) ->Set[Tuple[str, Optional[str], int]]:
        linhas = self.conn.execute(
            """
            SELECT i.nome AS indicador, l.codigo AS linha, v.ano AS ano
            FROM valor_indicador v
            JOIN indicador i ON i.id_indicador = v.id_indicador
            LEFT JOIN linha l ON l.id_linha = v.id_linha
            """
        ).fetchall()
        
        return {(l["indicador"], l["linha"], l["ano"]) for l in linhas}

    def save_all( self, id_importacao: int, valores : Iterable[ValorIndicador]) -> None:
        
        """INSERT de todos os valores, sem commits
        
        Devido a forma como escolhi gravar o total de cada linha, o indicador e a linha tem sempre de exisitr (KeyError se não existirem).
        
        """
        ids_indicador = { r["nome"]: r["id_indicador"] for r in self.conn.execute("SELECT id_indicador, nome FROM indicador")}

        ids_linha = {r["codigo"] : r["id_linha"] for r in self.conn.execute("SELECT id_linha, codigo FROM linha")}

        self.conn.executemany(
            """
            INSERT INTO valor_indicador
                (id_importacao, id_indicador, id_linha, ano, valor)
            VALUES (?,?,?,?,?)
            """,
            [
                (
                    id_importacao,
                    ids_indicador[v.indicador.nome],
                    ids_linha[v.linha.codigo] if v.linha else None,
                    v.ano,
                    v.valor,
                )
                for v in valores
            ],
        )

    def listing(self) -> List[ValorIndicador]:
        
        """Apresenta todos os valores, por ordem de inserção (= ordem do ficheiro)."""

        linhas=self.conn.execute(
            """
            SELECT i.nome AS indicador, i.unidade AS unidade,
                l.codigo AS linha_codigo, l.nome AS linha_nome,
                v.ano AS ano, v.valor AS valor
            FROM valor_indicador v
            JOIN indicador i ON i.id_indicador = v.id_indicador
            LEFT JOIN linha l ON l.id_linha = v.id_linha
            ORDER BY v.id_valor
            """
        ).fetchall()
        return [
            ValorIndicador(
                indicador=Indicador(nome=l["indicador"], unidade = l["unidade"]),
                linha=(
                    None
                    if l["linha_codigo"] is None
                    else Linha(codigo=l["linha_codigo"], nome=l["linha_nome"])
                ),
                ano=l["ano"],
                valor=l["valor"],
            )
            for l in linhas
        ]
