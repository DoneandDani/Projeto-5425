
from __future__ import annotations

import sqlite3
from typing import Dict, List, Optional

from metro_em_numeros.domain.erros import (
    InvalidData,
    DoubleRegistry,
    RegistryInUse,
    RegistryNotFound,
)
from metro_em_numeros.domain.modelos import Linha, ModoTransporte
from metro_em_numeros.repositories.linha_repository import LinhaRepository
from metro_em_numeros.repositories.modo_repository import ModoRepository


class LinhaService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn  # o serviço controla a transação
        self.linhas = LinhaRepository(conn)
        self.modos = ModoRepository(conn)

    def list_linhas(self) -> List[Linha]:
        return self.linhas.l()

    def list_modes(self) -> List[ModoTransporte]:
        return self.modos.show_list()

    def name_of_modes(self) -> Dict[int, str]:
        return {m.id: m.nome for m in self.modos.show_list()}

    def get_line(self, id_linha: int) -> Linha:
        linha = self.linhas.get_linha(id_linha)
        if linha is None:
            raise RegistryNotFound("A linha não existe.")
        return linha

    def create_line(self, codigo: str, nome: str, id_modo: Optional[int]) -> Linha:
        linha = Linha(codigo=codigo, nome=nome, id_modo=id_modo)  # valida
        self._verify_mode(id_modo)
        if self.linhas.search_by_code(linha.codigo) is not None:
            raise DoubleRegistry("Já existe uma linha com este código.")
        with self.conn:
            return self.linhas.save_linha(linha)

    def edit_line(self, id_linha: int, nome: str, id_modo: Optional[int]) -> Linha:
        atual = self.get_line(id_linha)
        # o código não muda: a importação reconhece as linhas por ele
        linha = Linha(id=id_linha, codigo=atual.codigo, nome=nome, id_modo=id_modo)
        self._verify_mode(id_modo)
        with self.conn:
            return self.linhas.save_linha(linha)

    def delete_line(self, id_linha: int) -> None:
        self.get_line(id_linha)
        total = self.linhas.count_values(id_linha)
        if total:
            raise RegistryInUse(
                f"Não é possível eliminar: a linha tem {total} valor(es) associado(s)."
            )
        with self.conn:
            self.linhas.delete(id_linha)

    def _verify_mode(self, id_modo: Optional[int]) -> None:
        if id_modo is None or self.modos.get_modo(id_modo) is None:
            raise InvalidData("Escolha um modo de transporte válido.")