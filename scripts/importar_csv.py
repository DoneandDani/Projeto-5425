
"""Importa um CSV para a base de dados"""


import argparse
import sys
from pathlib import Path

from metro_em_numeros.config import obter_caminho_bd
from metro_em_numeros.database import initialize, connect
from metro_em_numeros.domain.erros import RepeatedImport, InvalidImport
from metro_em_numeros.services.importacao_service import ImportacaoService

CSV_PADRAO = Path("data/data_2016_2024.csv")


def main() -> int:
    parser = argparse.ArgumentParser(description="Importar CSV com dados")
    parser.add_argument("csv", nargs="?", type=Path, default=CSV_PADRAO)
    argumentos = parser.parse_args()

    caminho_bd = obter_caminho_bd()
    initialize(caminho_bd)
    conn= connect(caminho_bd)

    try:
        importacao = ImportacaoService(conn).import_file(argumentos.csv)
    
    except FileNotFoundError:
        print(f"Erro: ficheiro não encontrado: {argumentos.csv}", file=sys.stderr)
        return 1
    
    except InvalidImport as erro:
        print ("Importação cancelada. Nada foi gravado.", file=sys.stderr)
        for mensagem in erro.erros:
            print(f" - {mensagem}", file=sys.stderr)
        return 1

    except RepeatedImport as erro:
        print(erro)
        return 0
    finally:
        conn.close()


    print(f"Importação concluída: {importacao.num_registos} registos" 
          f"importação #{importacao.id}.")

    return 0

if __name__ == "__main__":
    sys.exit(main())

    