
"""Página de impacto ambiental (estimativa)."""
from fastapi import APIRouter, Request

from metro_em_numeros.domain.erros import InvalidData, InvalidImport
from metro_em_numeros.services.impacto_service import ImpactoService
from metro_em_numeros.web.comum import open_connection, templates

router = APIRouter(tags=["impacto"])


@router.get("/impacto")
def page_impact(request: Request, desvio: float = 100.0):
    contexto = {"disponivel": False, "desvio": 100.0, "mensagens": [],
                "fatores": [], "linhas": [], "total_balanco": None, "erro": None}
    status_code = 200
    with open_connection(request) as conn:
        try:
            contexto.update(
                ImpactoService(conn, request.app.state.fatores_path).estimate(desvio)
            )
        except InvalidData as erro:
            contexto["erro"] = str(erro)
            status_code = 422
        except InvalidImport as erro:
            contexto["erro"] = "Ficheiro de fatores inválido: " + "; ".join(erro.erros)
            status_code = 422
    return templates.TemplateResponse(
        request=request, name="impacto/lista.html",
        context=contexto, status_code=status_code,
    )