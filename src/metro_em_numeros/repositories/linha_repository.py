from __future__ import annotations

import sqlite3
from typing import List, Optional

from metro_em_numeros.domain.erros import (
    InvalidData,
    DoubleRegistry,
    RegistryInUse,
    RegistryNotFound,
)
from metro_em_numeros.domain.modelos import Linha

MODO_PADRAO = "Metro"
_COLUNAS = "id_linha, id_modo, codigo, nome"


def _for_object(linha: sqlite3.Row) -> Linha:
    return Linha(
        id=linha["id_linha"],
        id_modo=linha["id_modo"],
        codigo=linha["codigo"],
        nome=linha["nome"],
    )


class LinhaRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def make_sure(self, linha: Linha, modo: str = MODO_PADRAO) -> None:
        """Garante que o modo e a linha existem, se já não tiverem presentes."""
        self.conn.execute(
            "INSERT OR IGNORE INTO modo_transporte (nome) VALUES (?)",
            (modo,),
        )
        self.conn.execute(
            """
            INSERT OR IGNORE INTO linha (id_modo, codigo, nome)
            VALUES (
                (SELECT id_modo FROM modo_transporte WHERE nome = ?),
                ?, ?
            )
            """,
            (modo, linha.codigo, linha.nome),
        )

    def show_list(self) -> List[Linha]:
        linhas = self.conn.execute(
            f"SELECT {_COLUNAS} FROM linha ORDER BY codigo"
        ).fetchall()
        return [_for_object(l) for l in linhas]

    def get_linha(self, id_linha: int) -> Optional[Linha]:
        linha = self.conn.execute(
            f"SELECT {_COLUNAS} FROM linha WHERE id_linha = ?", (id_linha,)
        ).fetchone()
        return None if linha is None else _for_object(linha)

    def search_by_code(self, codigo: str) -> Optional[Linha]:
        linha = self.conn.execute(
            f"SELECT {_COLUNAS} FROM linha WHERE codigo = ?", (codigo,)
        ).fetchone()
        return None if linha is None else _for_object(linha)

    def count_values(self, id_linha: int) -> int:
        return self.conn.execute(
            "SELECT COUNT(*) FROM valor_indicador WHERE id_linha = ?", (id_linha,)
        ).fetchone()[0]

    # ---- escrita ----
    def save_linha(self, linha: Linha) -> Linha:
        """INSERT (sem id) ou UPDATE do nome e do modo (com id), sem commit."""
        try:
            if linha.id is None:
                cursor = self.conn.execute(
                    "INSERT INTO linha (id_modo, codigo, nome) VALUES (?, ?, ?)",
                    (linha.id_modo, linha.codigo, linha.nome),
                )
                id_linha = cursor.lastrowid
            else:
                cursor = self.conn.execute(
                    "UPDATE linha SET id_modo = ?, nome = ? WHERE id_linha = ?",
                    (linha.id_modo, linha.nome, linha.id),
                )
                if cursor.rowcount == 0:
                    raise RegistryNotFound("A linha não existe.")
                id_linha = linha.id
        except sqlite3.IntegrityError as erro:
            texto = str(erro)
            if "linha.codigo" in texto:
                raise DoubleRegistry("Já existe uma linha com este código.") from erro
            if "FOREIGN KEY" in texto or "NOT NULL" in texto:
                raise InvalidData("Escolha um modo de transporte válido.") from erro
            raise
        return Linha(
            id=id_linha, id_modo=linha.id_modo, codigo=linha.codigo, nome=linha.nome
        )

    def delete(self, id_linha: int) -> None:
        try:
            cursor = self.conn.execute(
                "DELETE FROM linha WHERE id_linha = ?", (id_linha,)
            )
        except sqlite3.IntegrityError as erro:
            if "FOREIGN KEY" in str(erro):
                raise RegistryInUse("Esta linha tem valores associados.") from erro
            raise
        if cursor.rowcount == 0:
            raise RegistryNotFound("A linha não existe.")


