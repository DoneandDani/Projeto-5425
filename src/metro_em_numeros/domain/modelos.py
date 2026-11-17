

#Conceitos e regras

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Optional,Tuple

from metro_em_numeros.domain.erros import InvalidData

ANO_MIN = 2000
ANO_MAX = 2030

UNIDADES_INDICADORES = {
    "Comboios": "10^3 comboios",
    "Comboios-Km" : "10^3 km",
    "Investimento": "10^3 euros",
    "Lugares-Km" : "10^3 lugares",
    "Passageiros" : "10^3 passageiros",
    "Passageiros-Km": "10^3 passageiros-Km"
}

_RE_CODIGO_LINHA= re.compile(r"MP - ([A-G])")
_RE_HASH=re.compile(r"[0-9a-f]{64}")

@dataclass(frozen=True)
class Linha:
    codigo: str
    nome: str

    def __post_init__(self):
        if not _RE_CODIGO_LINHA.fullmatch(self.codigo):
            raise InvalidData(f"Código da linnha inválido: '{self.codigo}.")
        if not self.nome.strip():
            raise InvalidData(f"Nome da linha obrigatório.")

    @classmethod
    def from_the_code(cls, codigo: str) -> "Linha":
        m = _RE_CODIGO_LINHA.fullmatch(codigo)
        if not m:
            raise InvalidData(f"Código da linnha inválido: '{codigo}.")
        return cls(codigo=codigo, nome=f"Linha {m.group(1)}")


@dataclass(frozen=True)
class Indicador:
    nome: str
    unidade: str

    def __post_init__(self):
        if not self.nome.strip():
            raise InvalidData("Nome do indicador obrigatório.")
        if not self.unidade.strip():
            raise InvalidData ("Unidade do indicador obrigatória.")

    @classmethod
    def known(cls,nome:str) -> "Indicador":
        if nome not in UNIDADES_INDICADORES:
            raise InvalidData(f"Indicador desconhecido: '{nome}.")
        return cls(nome=nome, unidade=UNIDADES_INDICADORES[nome])

@dataclass(frozen=True)
class ValorIndicador:

    """Classe com o valor anual de um dado indicador para uma linha ou para o total da rede
    
    Para linha: None significa total da rede
    Para valor: Nono significa sem dados (que é diferente de ser 0)

    """
    indicador: Indicador
    linha: Optional[Linha]
    ano: int 
    valor: Optional[float]

    def __post_init__(self):
        if not (ANO_MIN<=self.ano<ANO_MAX):
            raise InvalidData( f"Ano {self.ano} fora do intervalo {ANO_MIN} - {ANO_MAX}.")
        if self.valor is not None and not math.isfinite(self.valor):
            raise InvalidData("O valor tem de ser finito.")

    @property
    def e_total(self) ->bool:
        return self.linha is None

    @property
    def key(self) ->Tuple[str, Optional[str], int]:
        
        return ( self.indicador.nome, self.linha.codigo if self.linha else None, self.ano,)


@dataclass(frozen=True)
class Importacao:
    id: Optional[int] 
    nome_ficheiro: str
    hash_sha256: str
    fonte: str
    num_registos: int
    data_importacao: Optional[str] = None

    def __post_init__(self):
        if not self.nome_ficheiro.strip():
            raise InvalidData("Nome do ficheiro obrigatório.")
        if not _RE_HASH.fullmatch(self.hash_sha256):
            raise InvalidData("Hash SHA-256 deve ter 64 caracateres hexadecimais.")
        if not self.fonte.strip():
            raise InvalidData("Fonte obrigatória.")
        if self.num_registos<0:
            raise InvalidData("Número de registos tem que ser positivo.")








