

from __future__ import annotations

import sqlite3
from typing import Optional

from metro_em_numeros.repositories.importacao_repository import ImportacaoRepository
from metro_em_numeros.repositories.valor_repository import ValorRepository

SEM_DADOS = "-"
NOME_TOTAL = "Total (rede)"

def value_formating(valor: Optional[float]) -> str:
    """Formatar os dados para serem mais legíveis e passar None -> '-' """
    if valor is None:
        return SEM_DADOS
    texto = f"{valor:,.1f}"
    return texto.replace(",", "\u00a0").replace(".", ",")

class ConsultaService:
    def __init__(self, conn: sqlite3.Connection):
        self.valores= ValorRepository(conn)
        self.importacoes = ImportacaoRepository(conn)

    def get_tables(self) ->dict:
        valores =self.valores.listing()
        ultima =self.importacoes.last()
        
        if not valores or ultima is None:
            return {"tabelas" : [], "periodo": None, "ultima_importacao": None}

        por_indicador: dict = {}
        for  v in valores:
            grupo = por_indicador.setdefault( v.indicador.nome, {"unidade": v.indicador.unidade, "linhas": {}, "anos": set()},)
            grupo["anos"].add(v.ano)
            codigo = v.linha.codigo if v.linha else None
            grupo["linhas"].setdefault(codigo, {})[v.ano] = v.valor

        todos_os_anos = sorted({v.ano for v in valores})
        tabelas =[]

        for nome, grupo in por_indicador.items():
            anos = sorted(grupo["anos"])
            tabelas.append({
                "indicador" :nome,
                "unidade" : grupo["unidade"],
                "anos" : anos,
                "linhas" : [
                    {
                        "nome" : NOME_TOTAL if codigo is None else codigo,
                        "e_total": codigo is None,
                        "valores" : [value_formating(mapa.get(a)) for a in anos],
                    }
                    for codigo, mapa in grupo["linhas"].items()
                ],
            }) 

        return{
            "tabelas" : tabelas,
            "periodo": f"{todos_os_anos[0]} - {todos_os_anos[-1]}",
            "ultima_importacao" : ultima,
        }