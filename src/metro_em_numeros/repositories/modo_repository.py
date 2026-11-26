

from __future__ import annotations

import sqlite3
from typing import List, Optional

from metro_em_numeros.domain.erros import DoubleRegistry, RegistryInUse, RegistryNotFound
from metro_em_numeros.domain.modelos import ModoTransporte


def _for_object(linha: sqlite3.Row) -> ModoTransporte:
    return ModoTransporte(
        id=linha["id_modo"], nome=linha["nome"], descricao=linha["descricao"]
    )


class ModoRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def show_list(self) -> List[ModoTransporte]:
        linhas = self.conn.execute(
            "SELECT id_modo, nome, descricao FROM modo_transporte ORDER BY nome"
        ).fetchall()
        return [_for_object(l) for l in linhas]

    def get_mode(self, id_modo: int) -> Optional[ModoTransporte]:
        linha = self.conn.execute(
            "SELECT id_modo, nome, descricao FROM modo_transporte WHERE id_modo = ?",
            (id_modo,),
        ).fetchone()
        return None if linha is None else _for_object(linha)

    def search_by_name(self, nome: str) -> Optional[ModoTransporte]:
        linha = self.conn.execute(
            "SELECT id_modo, nome, descricao FROM modo_transporte WHERE nome = ?",
            (nome,),
        ).fetchone()
        return None if linha is None else _for_object(linha)

    def count_lines(self, id_modo: int) -> int:
        return self.conn.execute(
            "SELECT COUNT(*) FROM linha WHERE id_modo = ?", (id_modo,)
        ).fetchone()[0]

    def save(self, modo: ModoTransporte) -> ModoTransporte:
        """INSERT (sem id) ou UPDATE (com id), sem commit."""
        try:
            if modo.id is None:
                cursor = self.conn.execute(
                    "INSERT INTO modo_transporte (nome, descricao) VALUES (?, ?)",
                    (modo.nome, modo.descricao),
                )
                id_modo = cursor.lastrowid
            else:
                cursor = self.conn.execute(
                    "UPDATE modo_transporte SET nome = ?, descricao = ? WHERE id_modo = ?",
                    (modo.nome, modo.descricao, modo.id),
                )
                if cursor.rowcount == 0:
                    raise RegistryNotFound("O modo de transporte não existe.")
                id_modo = modo.id
        except sqlite3.IntegrityError as erro:
            if "modo_transporte.nome" in str(erro):
                raise DoubleRegistry(
                    "Já existe um modo de transporte com este nome."
                ) from erro
            raise
        return ModoTransporte(id=id_modo, nome=modo.nome, descricao=modo.descricao)

    def delete(self, id_modo: int) -> None:
        try:
            cursor = self.conn.execute(
                "DELETE FROM modo_transporte WHERE id_modo = ?", (id_modo,)
            )
        except sqlite3.IntegrityError as erro:
            if "FOREIGN KEY" in str(erro):
                raise RegistryInUse(
                    "Este modo de transporte tem linhas associadas."
                ) from erro
            raise
        if cursor.rowcount == 0:
            raise RegistryNotFound("O modo de transporte não existe.")