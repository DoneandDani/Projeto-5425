"""Renderiza os templates sem FastAPI (url_for é simulado)."""
from pathlib import Path

import pytest
from jinja2 import Environment, FileSystemLoader

import metro_em_numeros
from metro_em_numeros.domain.impacto import FatorEmissao
from metro_em_numeros.domain.modelos import Linha, ModoTransporte

TEMPLATES = Path(metro_em_numeros.__file__).resolve().parent / "templates"


def renderizar(modelo, **contexto):
    ambiente = Environment(loader=FileSystemLoader(str(TEMPLATES)), autoescape=True)
    ambiente.globals["url_for"] = lambda nome_, path: "/static" + path
    return ambiente.get_template(modelo).render(**contexto)


def test_base_tem_a_navegacao():
    html = renderizar("linhas/lista.html", linhas=[], nomes_modos={}, erro=None)
    for destino in ("/analise", "/graficos", "/impacto", "/linhas", "/modos", "/importar"):
        assert f'href="{destino}"' in html


# ---- linhas ----
def test_lista_de_linhas():
    linha = Linha(id=7, codigo="MP - A", nome="Linha A", id_modo=1)
    html = renderizar("linhas/lista.html", linhas=[linha], nomes_modos={1: "Metro"}, erro=None)
    assert "MP - A" in html and "Metro" in html
    assert 'href="/linhas/7/editar"' in html
    assert 'action="/linhas/7/eliminar"' in html


def test_lista_de_linhas_vazia_e_com_erro():
    html = renderizar("linhas/lista.html", linhas=[], nomes_modos={}, erro="Algo falhou")
    assert "Ainda não existem linhas" in html
    assert 'role="alert"' in html and "Algo falhou" in html


def test_formulario_de_linha_em_edicao():
    modos = [ModoTransporte(id=1, nome="Metro"), ModoTransporte(id=2, nome="Elétrico")]
    html = renderizar(
        "linhas/formulario.html", titulo="Editar linha", acao="/linhas/7", editar=True,
        codigo="MP - A", nome="Linha A", id_modo=2, modos=modos, erro=None,
    )
    assert "readonly" in html
    assert '<option value="2" selected>Elétrico</option>' in html
    assert '<option value="1" selected>' not in html


def test_formulario_de_linha_nova_nao_e_readonly():
    html = renderizar(
        "linhas/formulario.html", titulo="Registar linha", acao="/linhas", editar=False,
        codigo="", nome="", id_modo=None, modos=[], erro=None,
    )
    assert "readonly" not in html


def test_valores_do_utilizador_sao_escapados():
    html = renderizar(
        "linhas/formulario.html", titulo="x", acao="/linhas", editar=False,
        codigo="", nome='"><script>alert(1)</script>', id_modo=None, modos=[],
        erro="<b>erro</b>",
    )
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html and "&lt;b&gt;erro" in html


# ---- modos ----
def test_lista_de_modos():
    modos = [ModoTransporte(id=1, nome="Metro", descricao=None)]
    html = renderizar("modos/lista.html", modos=modos, erro=None)
    assert "Metro" in html and 'action="/modos/1/eliminar"' in html
    assert "—" in html  # sem descrição


def test_formulario_de_modo():
    html = renderizar("modos/formulario.html", titulo="Registar", acao="/modos",
                      nome="Metro", descricao="", erro=None)
    assert 'action="/modos"' in html and 'value="Metro"' in html


# ---- gráficos ----
def test_pagina_de_graficos():
    opcoes = [{"chave": "passageiros", "titulo": "Passageiros", "derivada": False},
              {"chave": "ocupacao", "titulo": "Taxa de ocupação", "derivada": True}]
    html = renderizar("graficos/lista.html", opcoes=opcoes)
    assert '<option value="ocupacao">Taxa de ocupação (calculado)</option>' in html
    assert "/static/js/chart.umd.min.js" in html and "/static/js/graficos.js" in html


def test_pagina_de_graficos_sem_dados():
    assert "Ainda não existem dados" in renderizar("graficos/lista.html", opcoes=[])


# ---- importar ----
@pytest.mark.parametrize(
    "tipo, texto, classe",
    [("sucesso", "Concluída", "sucesso"), ("info", "Já importado", "aviso"),
     ("erro", "valor inválido", "erro")],
)
def test_pagina_de_importar(tipo, texto, classe):
    html = renderizar("importar/formulario.html", tipo=tipo, mensagens=[texto])
    assert texto in html and f'class="{classe}"' in html
    assert 'enctype="multipart/form-data"' in html


# ---- impacto ----
BASE = {"desvio": 100.0, "mensagens": [], "fatores": [], "linhas": [],
        "total_balanco": None, "erro": None}


def test_impacto_indisponivel():
    html = renderizar("impacto/lista.html", **{**BASE, "disponivel": False,
                      "mensagens": ["Falta preencher o fator de emissão de: carro."]})
    assert "Falta preencher" in html
    assert "Balanço de emissões por ano" not in html


def test_impacto_disponivel_mostra_fontes_e_limitacoes():
    fatores = [FatorEmissao("carro", 100.0, 2018, "TESTE", "Fonte de teste", "http://x")]
    linhas = [{"ano": 2024, "milhoes_pkm": "477,6", "metro_t": "1",
               "alternativa_t": "2", "balanco_t": "3"}]
    html = renderizar("impacto/lista.html", **{**BASE, "disponivel": True,
                      "linhas": linhas, "total_balanco": "3", "fatores": fatores})
    assert "Balanço de emissões por ano" in html and "477,6" in html
    assert "100,0 g CO₂e" in html and "Fonte de teste" in html
    assert "Limitações" in html and "médias europeias" in html


def test_impacto_mostra_erro_do_utilizador():
    html = renderizar("impacto/lista.html", **{**BASE, "disponivel": False,
                      "erro": "A percentagem tem de estar entre 0 e 100."})
    assert "entre 0 e 100" in html