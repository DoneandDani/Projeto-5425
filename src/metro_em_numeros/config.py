

import os
from pathlib import Path

def obter_caminho_bd() -> Path:
    valor = os.getenv("Metro_DB_PATH", "data/metro.db")
    return Path(valor)

