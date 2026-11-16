
class InvalidData(ValueError):
    """Os dados de um objeto não cumpre as regras."""


class InvalidImport(Exception):
    """Houve problemas com a importação ou com o ficheiro. Guarda as mensagens."""

    def __init__(self, erros):
        self.erros = list(erros)
        super().__init__(";".join(self.erros))

class RepeatedImport(Exception):
    """Repetição da importação do ficheiro."""