
"""Séries temporais prontas a apresentar (tabelas e gráficos)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class LinhaSerie:
    nome: str                       # 'Total (rede)' ou 'MP - A'
    e_total: bool
    valores: List[Optional[float]]  # um valor por ano (None = sem dados)


@dataclass(frozen=True)
class Serie:
    chave: str      # identificador em URLs, ex.: 'passageiros'
    titulo: str
    unidade: str
    anos: List[int]
    linhas: List[LinhaSerie]
    derivada: bool = False  # True se for calculada a partir de outros indicadores
    casas: int = 1          # casas decimais ao apresentar
    nota: str = ""