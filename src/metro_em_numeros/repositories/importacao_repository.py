

from __future__ import annotations

import sqlite3
from typing import Optional

from metro_em_numeros.domain.erros import RepeatedImport
from metro_em_numeros.domain.modelos import Importacao

_COLUNAS = ("id_importacao, nome_ficheiro, hash_shad246, fonte,"
            "num_registos, data_importacao"
            )

def _for_object(linha:sqlite3.Row) -> Importacao:
    
    return Importacao(
        id=linha["id_importacao"],
        nome_ficheiro=linha["nome_ficheiro"],
        hash_sha256=linha["hash_sha256"],
        fonte=linha["fonte"],
        num_registos=linha["num_registos"],
        data_importacao=linha["data_importacao"],
    )

class ImportacaoRepository:
    
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def search_with_hash(self, hash_sha256: str) -> Optional[Importacao]:
        linha = self.conn.execute( f"SELECT {_COLUNAS} FROM importacao WHERE hash_sha256 = ?", (hash_sha256,),).fetchone()
        return None if linha is None else _for_object(linha)

    def last(self) -> Optional[Importacao]:
        linha= self.conn.execute( f"SELECT {_COLUNAS} FROM importacao ORDER BY id_importacao DESC LIMIT 1").fetchone()
        return None if linha is None else _for_object(linha)

    def make_save(self, importacao: Importacao) -> Importacao:
        
        """ Para um INSERT sem commit. Devolve a importação com o id e data."""
        try:
            cursor = self.conn.execute(
                """
                INSERT INTO importacao
                    (nome_ficheiro, hash_sha256, fonte, num_registos)
                VALUES (?,?,?,?)
                """,
                (
                    importacao.nome_ficheiro,
                    importacao.hash_sha256,
                    importacao.fonte,
                    importacao.num_registos,
                ),
            )
        except sqlite3.IntegrityError as erro:
            if "importacao.hash_sha256" in str(erro):
                raise RepeatedImport( "Ficheiro já importado.") from erro
            raise
        linha =self.conn.execute( f"SELECT {_COLUNAS} FROM importacao WHERE id_importacao =?", (cursor.lastrowid,),).fetchone()
        return _for_object(linha)

    