
"""Leitura dos fatores de emissão (data/fatores_emissao.csv)."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List

from metro_em_numeros.domain.erros import InvalidData, InvalidImport
from metro_em_numeros.domain.impacto import FatorEmissao

COLUNAS = ["modo", "g_co2e_por_pkm", "ano_referencia", "ambito", "fonte", "url"]


def _field(linha: dict, nome: str) -> str:
    return (linha.get(nome) or "").strip()


def read_factors(caminho) -> Dict[str, FatorEmissao]:
    """Devolve os fatores por modo ou levanta InvalidImport."""
    erros: List[str] = []
    fatores: Dict[str, FatorEmissao] = {}

    with open(Path(caminho), newline="", encoding="utf-8-sig") as ficheiro:
        leitor = csv.DictReader(ficheiro)
        em_falta = [c for c in COLUNAS if c not in (leitor.fieldnames or [])]
        if em_falta:
            raise InvalidImport(
                [f"Faltam colunas no ficheiro de fatores: {', '.join(em_falta)}."]
            )
        for linha in leitor:
            n = leitor.line_num
            try:
                texto = _field(linha, "g_co2e_por_pkm")
                fator = FatorEmissao(
                    modo=_field(linha, "modo"),
                    g_co2e_por_pkm=float(texto) if texto else None,
                    ano_referencia=int(_field(linha, "ano_referencia")),
                    ambito=_field(linha, "ambito"),
                    fonte=_field(linha, "fonte"),
                    url=_field(linha, "url"),
                )
            except InvalidData as erro:
                erros.append(f"linha {n}: {erro}")
                continue
            except ValueError:
                erros.append(
                    f"linha {n}: valor ou ano de referência inválido "
                    "(use ponto como separador decimal)."
                )
                continue
            if fator.modo in fatores:
                erros.append(f"linha {n}: o modo '{fator.modo}' está repetido.")
                continue
            fatores[fator.modo] = fator

    if erros:
        raise InvalidImport(erros)
    return fatores