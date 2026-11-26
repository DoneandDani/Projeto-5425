
"""Formatação de números"""

from __future__ import annotations

from typing import Optional

SEM_DADOS = "—"


def format_value(valor: Optional[float], casas: int = 1) -> str:
    """5274.2 -> '5 274,2'. None -> '—' (sem dados, não é zero)."""
    if valor is None:
        return SEM_DADOS
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "\u00a0").replace(".", ",")