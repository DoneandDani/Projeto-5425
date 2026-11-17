"""Teste de uma importação completa: CSV -> validação -> SQLite"""

import sqlite3
import pytest


from metro_em_numeros.domain.erros import RepeatedImport, InvalidImport
from metro_em_numeros.repositories.valor_repository import ValorRepository
from metro_em_numeros.services.importacao_service import ImportacaoService, calculate_hash

TABELAS = ("valor_indicador", "importacao", "linha", "indicador", "modo_transporte" )

def test_importa_o_ficheiro_real(conn, csv_real, count_lines):
    importacao = ImportacaoService(conn).import_file(csv_real)
    assert importacao.id is not None
    assert importacao.num_registos == 432
    assert importacao.data_importacao is not None
    assert count_lines("valor_indicador") ==432
    assert count_lines("importacao") ==1

def test_criar_as_entidades_de_referencia(conn, csv_real, count_lines):
    ImportacaoService(conn).import_file(csv_real)
    assert count_lines("modo_transporte") ==1
    assert count_lines("linha") ==7
    assert count_lines("indicador") ==6


def test_totais_ficam_com_linha_nula(conn, csv_real):
    ImportacaoService(conn).import_file(csv_real)
    totais = conn.execute( "SELECT COUNT(*) FROM valor_indicador WHERE id_linha IS NULL").fetchone()[0]
    assert totais == 6 *9

def test_valores_guardados_estao_corretos(conn, csv_real):
    ImportacaoService(conn).import_file(csv_real)
    valores = {v.key: v.valor for v in ValorRepository(conn).listing()}
    assert valores[("Passageiros", "MP - D" , 2024)] ==35069.0
    assert valores["Passageiros", None, 2024] == 89780.4

def test_celula_vazia_fica_nula_e_nao_zero(conn, csv_small):
    ImportacaoService(conn).import_file(csv_small)
    valores = {v.key: v.valor for v in ValorRepository(conn).listing()}
    assert valores[("Passageiros", "MP - G", 2024)] is None

def test_repetir_o_mesmo_ficheiro_nao_duplica(conn, csv_real, count_lines):
    servico =ImportacaoService(conn)
    servico.import_file(csv_real)
    with pytest.raises(RepeatedImport, match= "já foi importado"):
        servico.import_file(csv_real)
    assert count_lines("valor_indicador") ==432
    assert count_lines("importacao") == 1


def test_ficheiro_diferente_com_as_mesmas_chaves_e_rejeitado(conn,write_csv, text_csv_small,count_lines):
    servico= ImportacaoService(conn)
    servico.import_file(write_csv(text_csv_small, "a.csv"))
    outro = text_csv_small.replace("79,140.70", "79,000.00")
    with pytest.raises(InvalidImport, match="já existem"):
        servico.import_file(write_csv(outro, "b.csv"))
    assert count_lines("valor_indicador") == 6
    assert count_lines("importacao") == 1

def test_falha_a_meio_faz_rollback_de_tudo(conn, csv_small, count_lines, monkeypatch):
    def failure(*args, **kwargs):
        raise sqlite3.OperationalError("falha simulada")

    monkeypatch.setattr(ValorRepository, "save_all", failure)
    with pytest.raises(sqlite3.OperationalError):
        ImportacaoService(conn).import_file(csv_small)

    for tabela in TABELAS:
        assert count_lines(tabela)==0


def test_hash_dependo_do_conteudo(write_csv):
    a = write_csv("x", "a.csv")
    b = write_csv("x", "b.csv")
    c = write_csv("y", "c.csv")
    assert calculate_hash(a) == calculate_hash(b)
    assert calculate_hash(a) != calculate_hash(c)
    assert len(calculate_hash(a)) ==64


def test_ficheiro_inexistente(conn,tmp_path):
    with pytest.raises(FileNotFoundError):
        ImportacaoService(conn).import_file(tmp_path/ "nao_exist.csv")



