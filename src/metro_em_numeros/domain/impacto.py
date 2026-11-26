
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

from metro_em_numeros.domain.erros import InvalidData


@dataclass(frozen=True)
class FatorEmissao:
    modo: str                         # ex.: 'carro', 'comboio'
    g_co2e_por_pkm: Optional[float]   # None = ainda por preencher
    ano_referencia: int
    ambito: str                       # ex.: 'EU-27, média'
    fonte: str
    url: str

    def __post_init__(self):
        if not self.modo.strip():
            raise InvalidData("O modo do fator de emissão é obrigatório.")
        if not self.fonte.strip():
            raise InvalidData("A fonte do fator de emissão é obrigatória.")
        valor = self.g_co2e_por_pkm
        if valor is not None and (not math.isfinite(valor) or valor <= 0):
            raise InvalidData("O fator de emissão tem de ser um número positivo.")

    @property
    def filled(self) -> bool:
        return self.g_co2e_por_pkm is not None