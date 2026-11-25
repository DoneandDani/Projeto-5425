
class InvalidData(ValueError):
    """Os dados de um objeto não cumpre as regras."""


class InvalidImport(Exception):
    """Houve problemas com a importação ou com o ficheiro. Guarda as mensagens."""

    def __init__(self, erros):
        self.erros = list(erros)
        super().__init__(";".join(self.erros))

class RepeatedImport(Exception):
    """Repetição da importação do ficheiro."""


class DoubleRegistry(Exception):
    """Já existe um registo com o mesmo valor único."""

class RegistryInUse(Exception):
    """Ooutros registos dependem do registo pedido."""

class RegistryNotFound(Exception):
    """Registo pedido não existe."""