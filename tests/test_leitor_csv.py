
"""Leitura do CSV não precisa da db"""

import pytest

from metro_em_numeros.domain.erros import InvalidImport
from metro_em_numeros.services.leitor_csv import read_csv

def test_ler_o_ficheiro_real(csv_real):
    valores = read_csv(csv_real)
    assert len(valores) == 6 * 8 * 9  # 6 indicadores x (total + 7 linhas) x 9 anos


def test_converte_numeros_com_separador_de_milhares(csv_small):
    valores = {v.key: v.valor for v in read_csv(csv_small)}
    assert valores[("Passageiros", None, 2024)] == 89780.4
    assert valores[("Passageiros", "MP - A", 2023)] == 12493.7


def test_celula_vazia_e_none(csv_small):
    valores = {v.key: v.valor for v in read_csv(csv_small)}
    assert valores[("Passageiros", "MP - G", 2024)] is None


def test_ignora_colunas_derivadas(csv_small):
    assert len(read_csv(csv_small)) == 3 * 2  # total + A + G, 2 anos


def test_valor_invalido(write_csv, text_csv_small):
    ficheiro = write_csv(text_csv_small.replace("13,981.40", "abc"))
    with pytest.raises(InvalidImport, match="valor inválido 'abc'"):
        read_csv(ficheiro)


def test_reporta_todos_os_erros(write_csv, text_csv_small):
    mau = text_csv_small.replace("13,981.40", "abc").replace("12,493.70", "xyz")
    with pytest.raises(InvalidImport) as excecao:
        read_csv(write_csv(mau))
    assert len(excecao.value.erros) == 2


def test_coluna_em_falta(write_csv):
    mau = "Indicador (10^3),2023,2024\r\nPassageiros,\"79,140.70\"\r\n"
    with pytest.raises(InvalidImport, match="faltam colunas"):
        read_csv(write_csv(mau))


def test_cabecalho_sem_anos(write_csv):
    with pytest.raises(InvalidImport, match="colunas de ano"):
        read_csv(write_csv("Indicador,Valor\r\nPassageiros,1\r\n"))


def test_ano_do_cabecalho_fora_do_intervalo(write_csv):
    with pytest.raises(InvalidImport, match="fora do intervalo"):
        read_csv(write_csv("Indicador (10^3),1800\r\nPassageiros,1\r\n"))


def test_indicador_desconhecido(write_csv, text_csv_small):
    with pytest.raises(InvalidImport, match="desconhecido"):
        read_csv(write_csv(text_csv_small + "Bananas,1,2,3\r\n"))


def test_linha_antes_de_qualquer_indicador(write_csv):
    with pytest.raises(InvalidImport, match="antes de qualquer indicador"):
        read_csv(write_csv("Indicador (10^3),2024\r\nMP - A,1\r\n"))


def test_ficheiro_vazio(write_csv):
    with pytest.raises(InvalidImport, match="vazio"):
        read_csv(write_csv(""))


def test_ficheiro_inexistente(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_csv(tmp_path / "nao_existe.csv")

def test_codigo_de_linha_fora_do_formato_do_csv(write_csv):
    mau = "Indicador (10^3),2024\r\nPassageiros,1\r\nMP - H,1\r\n"
    with pytest.raises(InvalidImport, match="desconhecido 'MP - H'"):
        read_csv(write_csv(mau))


def test_ficheiro_que_nao_e_utf8(tmp_path):
    caminho = tmp_path / "latin1.csv"
    caminho.write_bytes("Indicador (10^3),2024\nPassageiros,1\nMP - A,\xe9\n".encode("latin-1"))
    with pytest.raises(InvalidImport, match="UTF-8"):
        read_csv(caminho)