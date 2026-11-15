

from metro_em_numeros.config import obter_caminho_bd
from metro_em_numeros.database import initialize

if __name__ == "__main__":
    caminho= obter_caminho_bd()
    initialize(caminho)
    print(f"Base de dados pronta: {caminho}")

