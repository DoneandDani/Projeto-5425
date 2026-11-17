
"""Cordena a importação : ficheiros -> validação -> SQLite."""

from __future__ import annotations

import hashlib
import sqlite3

from pathlib import Path
from typing import List

from metro_em_numeros.domain.erros import RepeatedImport, InvalidImport
from metro_em_numeros.domain.modelos import Importacao, ValorIndicador
from metro_em_numeros.repositories.importacao_repository import ImportacaoRepository
from metro_em_numeros.repositories.indicador_repository import IndicadorRepository
from metro_em_numeros.repositories.linha_repository import LinhaRepository
from metro_em_numeros.repositories.valor_repository import ValorRepository
from metro_em_numeros.services.leitor_csv import read_csv

FONTE_PADRAO = "AMT Observatório - Metro do Porto: Redes, Ofertas e Procura"


def calculate_hash(caminho) -> str:
    
    """Calcula a SHA-256 do conteúdo do ficheiro (identifica-o de forma única)."""

    h=hashlib.sha256()
    with open(Path(caminho), "rb") as ficheiro:
        
        for bloco in iter(lambda:ficheiro.read(65536), b""):
            h.update(bloco)
    
    return h.hexdigest()


class ImportacaoService:
    def __init__(self, conn: sqlite3.Connection):
        # O serviço recebe não só repositórios mas também a ligação pois é ele que abre e fecha a transição.
        self.conn =conn
        self.importacoes = ImportacaoRepository(conn)
        self.linhas = LinhaRepository(conn)
        self.indicadores= IndicadorRepository(conn)
        self.valores= ValorRepository(conn)

    def import_file(self, caminho, fonte:str =FONTE_PADRAO) -> Importacao:
        
        """ Importa o ficheiro. Se existir qualquer erro, nada fica guardado."""
        caminho = Path(caminho)
        hash_sha256 = calculate_hash(caminho)

        anterior = self.importacoes.search_with_hash(hash_sha256)
        if anterior is not None:
            raise RepeatedImport(
                f"Este ficheiro já foi importado em {anterior.data_importacao} "
                f"(Importação #{anterior.id}). Nada foi alterado."
            )


        valores = read_csv(caminho)
        self._verify_conflicts(valores)

        importacao = Importacao(

            id=None,
            nome_ficheiro=caminho.name,
            hash_sha256=hash_sha256,
            fonte=fonte,
            num_registos=len(valores),

        )

        with self.conn:
            for linha in sorted({v.linha for v in valores if v.linha is not None}, key=lambda l:l.codigo,):
                self.linhas.make_sure(linha)

            for indicador in dict.fromkeys(v.indicador for v in valores):
                self.indicadores.make_sure(indicador)
            guardada = self.importacoes.make_save(importacao)
            self.valores.save_all(guardada.id, valores)
        return guardada


    def _verify_conflicts(self, valores: List[ValorIndicador]) -> None:
        
        existentes = self.valores.existing_keys()
        conflitos = [v for v in valores if v.key in existentes]
        
        if conflitos:
            indicador, linha, ano = conflitos[0].key
            raise InvalidImport([
                f"{len(conflitos)} registos já existem na base de dados"
                f"(ex.: {indicador} / {linha or 'Total'} / {ano}). "
                "Nada foi gravado."
            ])