'''Calculo dos indicadores derivados'''

from __future__ import annotations

from typing import Optional


def division(
    numerador: Optional[float], denominador: Optional[float], fator: float = 1.0
) -> Optional[float]:
    """numerador / denominador * fator. None se faltar um valor ou se dividir por zero."""
    if numerador is None or denominador is None or denominador == 0:
        return None
    return numerador / denominador * fator


def variation_percent(
    anterior: Optional[float], atual: Optional[float]
) -> Optional[float]:
    """Variação em % entre dois anos. None se faltar um valor ou o anterior for 0."""
    if anterior is None or atual is None or anterior == 0:
        return None
    return (atual - anterior) / anterior * 100