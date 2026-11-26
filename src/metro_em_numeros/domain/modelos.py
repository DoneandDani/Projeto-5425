

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

_RE_HASH=re.compile(r"[0-9a-f]{64}")

@dataclass(frozen=True)
class ModoTransporte:
    nome: str
    descricao: Optional[str] = None
    id: Optional[int] = None  # None antes de guardar

    def __post_init__(self):
        nome = " ".join(self.nome.split())
        descricao = (self.descricao or "").strip() or None
        if not nome:
            raise InvalidData("O nome do modo de transporte é obrigatório.")
        if len(nome) > 100:
            raise InvalidData("O nome do modo de transporte não pode exceder 100 caracteres.")
        if descricao is not None and len(descricao) > 255:
            raise InvalidData("A descrição não pode exceder 255 caracteres.")
        object.__setattr__(self, "nome", nome)
        object.__setattr__(self, "descricao", descricao)


@dataclass(frozen=True)
class Linha:
    codigo: str  # ex.: 'MP - A'
    nome: str    # ex.: 'Linha A'
    id: Optional[int] = None
    id_modo: Optional[int] = None

    def __post_init__(self):
        codigo = self.codigo.strip()
        nome = " ".join(self.nome.split())
        if not codigo:
            raise InvalidData("O código da linha é obrigatório.")
        if len(codigo) > 20:
            raise InvalidData("O código da linha não pode exceder 20 caracteres.")
        if not nome:
            raise InvalidData("O nome da linha é obrigatório.")
        if len(nome) > 100:
            raise InvalidData("O nome da linha não pode exceder 100 caracteres.")
        object.__setattr__(self, "codigo", codigo)
        object.__setattr__(self, "nome", nome)




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








