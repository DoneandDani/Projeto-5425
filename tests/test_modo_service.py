
import pytest

from metro_em_numeros.domain.erros import (
    InvalidData,
    DoubleRegistry,
    RegistryInUse,
    RegistryNotFound,
)
from metro_em_numeros.services.linha_service import LinhaService
from metro_em_numeros.services.modo_service import ModoService


def test_criar_e_listar(conn):
    servico = ModoService(conn)
    criado = servico.create_mode("  Metro ligeiro ", "Rede do Porto")
    assert criado.id is not None
    assert criado.nome == "Metro ligeiro"
    assert [m.nome for m in servico.list_modes()] == ["Metro ligeiro"]


def test_nome_vazio_e_invalido(conn, contar):
    with pytest.raises(InvalidData):
        ModoService(conn).create_mode("   ")
    assert contar("modo_transporte") == 0


def test_nome_repetido(conn, contar):
    servico = ModoService(conn)
    servico.create_mode("Metro")
    with pytest.raises(DoubleRegistry):
        servico.create_mode("Metro")
    assert contar("modo_transporte") == 1


def test_editar(conn):
    servico = ModoService(conn)
    modo = servico.create_mode("Metro")
    editado = servico.edit_mode(modo.id, "Metro ligeiro", "Descrição nova")
    assert editado.nome == "Metro ligeiro"
    assert servico.get_mode(modo.id).descricao == "Descrição nova"


def test_editar_para_nome_de_outro_modo(conn):
    servico = ModoService(conn)
    servico.create_mode("Metro")
    autocarro = servico.create_mode("Autocarro")
    with pytest.raises(DoubleRegistry):
        servico.edit_mode(autocarro.id, "Metro")


def test_editar_mantendo_o_proprio_nome_e_permitido(conn):
    servico = ModoService(conn)
    modo = servico.create_mode("Metro")
    servico.edit_mode(modo.id, "Metro", "Só mudou a descrição")


def test_modo_inexistente(conn):
    servico = ModoService(conn)
    with pytest.raises(RegistryNotFound):
        servico.get_mode(999)
    with pytest.raises(RegistryNotFound):
        servico.edit_mode(999, "X")
    with pytest.raises(RegistryNotFound):
        servico.delete_mode(999)


def test_eliminar(conn, contar):
    servico = ModoService(conn)
    modo = servico.create_mode("Metro")
    servico.delete_mode(modo.id)
    assert contar("modo_transporte") == 0


def test_nao_elimina_modo_com_linhas(conn, contar):
    modo = ModoService(conn).create_mode("Metro")
    LinhaService(conn).create_line("MP - A", "Linha A", modo.id)
    with pytest.raises(RegistryInUse, match="1 linha"):
        ModoService(conn).delete_mode(modo.id)
    assert contar("modo_transporte") == 1