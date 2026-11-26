

from __future__ import annotations

import sqlite3
from typing import List

from metro_em_numeros.domain.erros import DoubleRegistry, RegistryInUse, RegistryNotFound
from metro_em_numeros.domain.modelos import ModoTransporte
from metro_em_numeros.repositories.modo_repository import ModoRepository


class ModoService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn  # o serviço controla a transação
        self.modos = ModoRepository(conn)

    def list_modes(self) -> List[ModoTransporte]:
        return self.modos.show_list()

    def get_mode(self, id_modo: int) -> ModoTransporte:
        modo = self.modos.get_mode(id_modo)
        if modo is None:
            raise RegistryNotFound("O modo de transporte não existe.")
        return modo

    def create_mode(self, nome: str, descricao: str = "") -> ModoTransporte:
        modo = ModoTransporte(nome=nome, descricao=descricao)  # valida
        if self.modos.search_by_name(modo.nome) is not None:
            raise DoubleRegistry("Já existe um modo de transporte com este nome.")
        with self.conn:
            return self.modos.save(modo)

    def edit_mode(self, id_modo: int, nome: str, descricao: str = "") -> ModoTransporte:
        self.get_mode(id_modo)
        modo = ModoTransporte(id=id_modo, nome=nome, descricao=descricao)
        existente = self.modos.search_by_name(modo.nome)
        if existente is not None and existente.id != id_modo:
            raise DoubleRegistry("Já existe um modo de transporte com este nome.")
        with self.conn:
            return self.modos.save(modo)

    def delete_mode(self, id_modo: int) -> None:
        self.get_mode(id_modo)
        total = self.modos.count_lines(id_modo)
        if total:
            raise RegistryInUse(
                f"Não é possível eliminar: o modo tem {total} linha(s) associada(s)."
            )
        with self.conn:
            self.modos.delete(id_modo)