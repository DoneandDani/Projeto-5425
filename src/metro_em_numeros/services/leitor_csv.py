

"""Leitura e validação de CSV.

Formato esperado:

    Indicador (10^3), 2016, ..., 2024, % do Total, Tx. Variação Anual %, ...
    Comboios, 353.00, ... <-total da rede
    MP - A, 75.00, ... <- linhas A a G do indicador acima

Os valores usam "," e "." como separador de milhares e decimal, respetivamente.
Células sem dados ficam como None.
Colunas derivadas de outras ( ex. % do Total) são ignoradas. 

"""

from __future__ import annotations

import csv
import math
import re

from pathlib import Path
from typing import List, Optional, Set, Tuple

from metro_em_numeros.domain.erros import InvalidData, InvalidImport
from metro_em_numeros.domain.modelos import (
    ANO_MAX,
    ANO_MIN,
    UNIDADES_INDICADORES,
    Indicador,
    Linha,
    ValorIndicador,
)

_RE_ANO = re.compile(r"\d{4}")

def _convert_value (texto:str) -> Optional[float]:
    texto =texto.strip()
    if texto == "":
        return None
    valor =float(texto.replace(",", "")) 
    if not math.isfinite(valor):
        raise ValueError(texto)
    return valor

def read_csv(caminho) -> List[ValorIndicador]:
    """Devolve os valores ou causa InvalidImport."""
    erros: List[str] = []
    valores : List [ValorIndicador] = []
    vistos: Set[Tuple] = set()

    with open(Path(caminho), newline="", encoding="utf-8-sig") as ficheiro:
        leitor = csv.reader(ficheiro)

        try:
            cabecalho= next(leitor)
        except StopIteration:
            raise InvalidImport(["Ficheiro vazio."])

        if not cabecalho or not cabecalho[0].strip().startswith("Indicador"):
            raise InvalidImport( ["Cabeçaloh inváldido a primeira coluna deve ser 'Indicador'."])

        colunas_ano= [
            (i, int(c.strip()))
            for i, c in enumerate(cabecalho)
            if _RE_ANO.fullmatch(c.strip())
        ]

        if not colunas_ano:
            raise InvalidImport(["Cabeçalho inválido: não foram encontradas colunas de ano."])

        fora =[ano for _, ano in colunas_ano if not (ANO_MIN<= ano<=ANO_MAX)]
        if fora:
            raise InvalidImport([f"Cabeçalho inválido: ano {fora[0]} fora do intervalo" f"{ANO_MIN} -{ANO_MAX}."])

        ultima_coluna = max( i for i, _ in colunas_ano)

        indicador_atual: Optional[Indicador] = None

        for celulas in leitor:
            n = leitor.line_num
            if not any(c.strip() for c in celulas):
                continue

            nome = celulas[0].strip()

            if nome in UNIDADES_INDICADORES:
                indicador_atual= Indicador.known(nome)
                linha =None
            else:
                try:
                    linha=Linha.from_the_code(nome)
                except InvalidData:
                    erros.append(f"linha {n}: indicador/linha desconhecida '{nome}'.")
                    continue
                if indicador_atual is None:
                    erros.append( f"linha {n}: {nome} aparece antes de qualquer indicador.")
                    continue

            if len(celulas) <= ultima_coluna:
                erros.append(
                    f"linha {n} ({nome}): faltam colunas "
                    f"(esperadas {ultima_coluna +1}, encontradas {len(celulas)})."
                )
                continue

            for i, ano in colunas_ano:
                
                try:
                    numero= _convert_value(celulas[i])
                except ValueError:
                    erros.append(f"linhas {n} ({nome}), {ano}: valor inválido '{celulas[i]}'.")
                    continue
                
                try:
                    valor =ValorIndicador(indicador_atual,linha, ano, numero)
                except InvalidData as erro:
                    erros.append(f"linha {n} ({nome}), {ano}: {erro}")
                    continue
                
                try:
                    valor= ValorIndicador(indicador_atual, linha, ano, numero)
                except InvalidData as erro:
                    erros.append(f"linha {n} ({nome}), {ano}: {erro}")
                    continue

                if valor.key in vistos:
                    erros.append( 
                        f"linha {n}: {indicador_atual.nome} / {nome} / {ano}"
                        "repetido no ficheirp."
                    )
                    continue
                vistos.add(valor.key)
                valores.append(valor)

    if erros:
        raise InvalidImport(erros)
    if not valores:
        raise InvalidImport(["O ficheiro não tem registos."])
    
    return valores
        

