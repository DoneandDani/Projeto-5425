

import os
from pathlib import Path

def obter_caminho_bd() -> Path:
    valor = os.getenv("Metro_DB_PATH", "data/metro.db")
    return Path(valor)

def obter_caminho_fatores() -> Path:
    valor = os.getenv("METRO_FATORES_PATH", "data/fatores_emissao.csv")
    return Path(valor)

