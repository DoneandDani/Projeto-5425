
"""Indicadores calculados, gráficos e a API JSON que alimenta os gráficos."""
from fastapi import APIRouter, HTTPException, Request

from metro_em_numeros.services.consulta_service import ConsultaService
from metro_em_numeros.services.series_service import SeriesService, serie_for_json
from metro_em_numeros.web.comum import open_connection, templates

router = APIRouter(tags=["analise"])


@router.get("/analise")
def page_analysis(request: Request):
    with open_connection(request) as conn:
        contexto = ConsultaService(conn).get_analysis()
    return templates.TemplateResponse(
        request=request, name="analise/lista.html", context=contexto
    )


@router.get("/graficos")
def page_graphs(request: Request):
    with open_connection(request) as conn:
        opcoes = ConsultaService(conn).options_graphs()
    return templates.TemplateResponse(
        request=request, name="graficos/lista.html", context={"opcoes": opcoes}
    )


@router.get("/api/series/{chave}")
def api_serie(request: Request, chave: str):
    with open_connection(request) as conn:
        serie = SeriesService(conn).cataloge().get(chave)
    if serie is None:
        raise HTTPException(status_code=404, detail="Série desconhecida.")
    return serie_for_json(serie)