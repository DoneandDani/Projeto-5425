
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import RedirectResponse

from metro_em_numeros.domain.erros import (
    InvalidData,
    DoubleRegistry,
    RegistryInUse,
    RegistryNotFound,
)
from metro_em_numeros.services.linha_service import LinhaService
from metro_em_numeros.web.comum import open_connection, integer_or_none, templates

router = APIRouter(prefix="/linhas", tags=["linhas"])
ERROS_PREVISTOS = (InvalidData, DoubleRegistry, RegistryInUse)


def _formulario(request, servico, titulo, acao, editar=False, codigo="", nome="",
                id_modo=None, erro=None, status_code=200):
    return templates.TemplateResponse(
        request=request,
        name="linhas/formulario.html",
        context={"titulo": titulo, "acao": acao, "editar": editar, "codigo": codigo,
                 "nome": nome, "id_modo": id_modo, "modos": servico.listar_modos(),
                 "erro": erro},
        status_code=status_code,
    )


def _list(request, servico, erro=None, status_code=200):
    return templates.TemplateResponse(
        request=request,
        name="linhas/lista.html",
        context={"linhas": servico.listar_linhas(),
                 "nomes_modos": servico.nomes_dos_modos(), "erro": erro},
        status_code=status_code,
    )


@router.get("")
def list_lines(request: Request):
    with open_connection(request) as conn:
        return _list(request, LinhaService(conn))


@router.get("/novo")
def formulario_nova(request: Request):
    with open_connection(request) as conn:
        return _formulario(request, LinhaService(conn), "Registar linha", "/linhas")


@router.post("")
def create_line(request: Request, codigo: str = Form(""), nome: str = Form(""),
                id_modo: str = Form("")):
    with open_connection(request) as conn:
        servico = LinhaService(conn)
        try:
            servico.create_line(codigo, nome, integer_or_none(id_modo))
        except ERROS_PREVISTOS as erro:
            return _formulario(request, servico, "Registar linha", "/linhas",
                               codigo=codigo, nome=nome, id_modo=id_modo,
                               erro=str(erro), status_code=422)
    return RedirectResponse(url="/linhas", status_code=303)


@router.get("/{id_linha}/editar")
def formulario_editar(request: Request, id_linha: int):
    with open_connection(request) as conn:
        servico = LinhaService(conn)
        try:
            linha = servico.get_line(id_linha)
        except RegistryNotFound as erro:
            raise HTTPException(status_code=404, detail=str(erro))
        return _formulario(request, servico, "Editar linha", f"/linhas/{id_linha}",
                           editar=True, codigo=linha.codigo, nome=linha.nome,
                           id_modo=linha.id_modo)


@router.post("/{id_linha}")
def editar_linha(request: Request, id_linha: int, nome: str = Form(""),
                 id_modo: str = Form("")):
    with open_connection(request) as conn:
        servico = LinhaService(conn)
        try:
            servico.edit_line(id_linha, nome, integer_or_none(id_modo))
        except RegistryNotFound as erro:
            raise HTTPException(status_code=404, detail=str(erro))
        except ERROS_PREVISTOS as erro:
            codigo = servico.get_line(id_linha).codigo
            return _formulario(request, servico, "Editar linha", f"/linhas/{id_linha}",
                               editar=True, codigo=codigo, nome=nome, id_modo=id_modo,
                               erro=str(erro), status_code=422)
    return RedirectResponse(url="/linhas", status_code=303)


@router.post("/{id_linha}/eliminar")
def delete_line(request: Request, id_linha: int):
    with open_connection(request) as conn:
        servico = LinhaService(conn)
        try:
            servico.delete_line(id_linha)
        except RegistryNotFound as erro:
            raise HTTPException(status_code=404, detail=str(erro))
        except RegistryInUse as erro:
            return _list(request, servico, str(erro), 422)
    return RedirectResponse(url="/linhas", status_code=303)