
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Request, UploadFile

from metro_em_numeros.domain.erros import RepeatedImport, InvalidImport
from metro_em_numeros.services.importacao_service import ImportacaoService
from metro_em_numeros.web.comum import open_connection, templates

router = APIRouter(tags=["importar"])
LIMITE_BYTES = 2 * 1024 * 1024  # 2 MB


def _reply(request, tipo=None, mensagens=(), status_code=200):
    return templates.TemplateResponse(
        request=request,
        name="importar/formulario.html",
        context={"tipo": tipo, "mensagens": list(mensagens)},
        status_code=status_code,
    )


@router.get("/importar")
def formulario_importar(request: Request):
    return _reply(request)


@router.post("/importar")
def load_csv(request: Request, ficheiro: UploadFile = File(...)):
    nome = Path(ficheiro.filename or "").name  # sem pastas: só o nome
    if not nome.lower().endswith(".csv"):
        return _reply(request, "erro", ["Escolha um ficheiro com extensão .csv."], 422)

    conteudo = ficheiro.file.read(LIMITE_BYTES + 1)
    if len(conteudo) > LIMITE_BYTES:
        return _reply(request, "erro", ["O ficheiro excede o limite de 2 MB."], 422)

    with tempfile.TemporaryDirectory() as pasta:
        caminho = Path(pasta) / nome
        caminho.write_bytes(conteudo)
        with open_connection(request) as conn:
            try:
                importacao = ImportacaoService(conn).import_file(caminho)
            except InvalidImport as erro:
                return _reply(request, "erro",
                                 ["Importação cancelada. Nada foi gravado."] + erro.erros, 422)
            except RepeatedImport as erro:
                return _reply(request, "info", [str(erro)])
    return _reply(
        request, "sucesso",
        [f"Importação concluída: {importacao.num_registos} registos "
         f"(importação #{importacao.id})."],
    )