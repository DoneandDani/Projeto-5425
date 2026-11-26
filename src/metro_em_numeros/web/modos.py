
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import RedirectResponse

from metro_em_numeros.domain.erros import (
    InvalidData,
    DoubleRegistry,
    RegistryInUse,
    RegistryNotFound,
)
from metro_em_numeros.services.modo_service import ModoService
from metro_em_numeros.web.comum import open_connection, templates

router = APIRouter(prefix="/modos", tags=["modos"])
ERROS_PREVISTOS = (InvalidData, DoubleRegistry, RegistryInUse)


def _formulario(request, titulo, acao, nome="", descricao="", erro=None, status_code=200):
    return templates.TemplateResponse(
        request=request,
        name="modos/formulario.html",
        context={"titulo": titulo, "acao": acao, "nome": nome,
                 "descricao": descricao, "erro": erro},
        status_code=status_code,
    )


def _list(request, servico, erro=None, status_code=200):
    return templates.TemplateResponse(
        request=request,
        name="modos/lista.html",
        context={"modos": servico.list_modes(), "erro": erro},
        status_code=status_code,
    )


@router.get("")
def list_modes(request: Request):
    with open_connection(request) as conn:
        return _list(request, ModoService(conn))


@router.get("/novo")
def formulario_novo(request: Request):
    return _formulario(request, "Registar modo de transporte", "/modos")


@router.post("")
def create_mode(request: Request, nome: str = Form(""), descricao: str = Form("")):
    with open_connection(request) as conn:
        try:
            ModoService(conn).create_mode(nome, descricao)
        except ERROS_PREVISTOS as erro:
            return _formulario(request, "Registar modo de transporte", "/modos",
                               nome, descricao, str(erro), 422)
    return RedirectResponse(url="/modos", status_code=303)


@router.get("/{id_modo}/editar")
def formulario_editar(request: Request, id_modo: int):
    with open_connection(request) as conn:
        try:
            modo = ModoService(conn).get_mode(id_modo)
        except RegistryNotFound as erro:
            raise HTTPException(status_code=404, detail=str(erro))
    return _formulario(request, "Editar modo de transporte", f"/modos/{id_modo}",
                       modo.nome, modo.descricao or "")


@router.post("/{id_modo}")
def edit_mode(request: Request, id_modo: int,
                nome: str = Form(""), descricao: str = Form("")):
    with open_connection(request) as conn:
        try:
            ModoService(conn).edit_mode(id_modo, nome, descricao)
        except RegistryNotFound as erro:
            raise HTTPException(status_code=404, detail=str(erro))
        except ERROS_PREVISTOS as erro:
            return _formulario(request, "Editar modo de transporte", f"/modos/{id_modo}",
                               nome, descricao, str(erro), 422)
    return RedirectResponse(url="/modos", status_code=303)


@router.post("/{id_modo}/eliminar")
def delete_mode(request: Request, id_modo: int):
    with open_connection(request) as conn:
        servico = ModoService(conn)
        try:
            servico.delete_mode(id_modo)
        except RegistryNotFound as erro:
            raise HTTPException(status_code=404, detail=str(erro))
        except RegistryInUse as erro:
            return _list(request, servico, str(erro), 422)
    return RedirectResponse(url="/modos", status_code=303)