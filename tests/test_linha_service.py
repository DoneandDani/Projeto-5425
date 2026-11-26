

import pytest

from metro_em_numeros.domain.erros import (
    InvalidData,
    DoubleRegistry,
    RegistryInUse,
    RegistryNotFound,
)
from metro_em_numeros.services.linha_service import LinhaService
from metro_em_numeros.services.modo_service import ModoService


@pytest.fixture
def modo(conn):
    return ModoService(conn).create_mode("Metro")


def test_criar_e_listar(conn, modo):
    servico = LinhaService(conn)
    criada = servico.create_line(" MP - A ", "  Linha   A", modo.id)
    assert criada.id is not None and criada.codigo == "MP - A"
    assert [l.codigo for l in servico.list_linhas()] == ["MP - A"]
    assert servico.name_of_modes() == {modo.id: "Metro"}


@pytest.mark.parametrize("id_modo", [None, 999])
def test_modo_invalido(conn, contar, id_modo):
    with pytest.raises(InvalidData, match="modo de transporte"):
        LinhaService(conn).create_line("MP - A", "Linha A", id_modo)
    assert contar("linha") == 0


def test_codigo_ou_nome_vazio(conn, modo):
    with pytest.raises(InvalidData):
        LinhaService(conn).create_line("", "Linha A", modo.id)
    with pytest.raises(InvalidData):
        LinhaService(conn).create_line("MP - A", "", modo.id)


def test_codigo_repetido(conn, modo, contar):
    servico = LinhaService(conn)
    servico.create_line("MP - A", "Linha A", modo.id)
    with pytest.raises(DoubleRegistry):
        servico.create_line("MP - A", "Outra", modo.id)
    assert contar("linha") == 1


def test_editar_muda_nome_e_modo_mas_nao_o_codigo(conn, modo):
    outro = ModoService(conn).create_mode("Elétrico")
    servico = LinhaService(conn)
    linha = servico.create_line("MP - A", "Linha A", modo.id)
    editada = servico.edit_line(linha.id, "Linha Azul", outro.id)
    assert (editada.codigo, editada.nome, editada.id_modo) == ("MP - A", "Linha Azul", outro.id)


def test_editar_linha_inexistente(conn, modo):
    with pytest.raises(RegistryNotFound):
        LinhaService(conn).edit_line(999, "X", modo.id)


def test_eliminar(conn, modo, contar):
    servico = LinhaService(conn)
    linha = servico.create_line("MP - A", "Linha A", modo.id)
    servico.delete_line(linha.id)
    assert contar("linha") == 0


def test_nao_elimina_linha_com_valores(conn_com_dados):
    servico = LinhaService(conn_com_dados)
    linha_a = next(l for l in servico.list_linhas() if l.codigo == "MP - A")
    with pytest.raises(RegistryInUse, match="valor"):
        servico.delete_line(linha_a.id)
    assert len(servico.list_linhas()) == 7


def test_linhas_importadas_aparecem_no_crud(conn_com_dados):
    servico = LinhaService(conn_com_dados)
    linhas = servico.list_linhas()
    assert [l.codigo for l in linhas] == [f"MP - {c}" for c in "ABCDEFG"]
    assert all(l.id_modo is not None for l in linhas)
    assert set(servico.name_of_modes().values()) == {"Metro"}