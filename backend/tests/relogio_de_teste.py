from datetime import datetime, timedelta


class RelogioDeTeste:
    """Relógio parado que o teste pode adiantar, simulando o tempo entre dois contatos.

    Com o relógio sempre parado, duas interações teriam exatamente o mesmo horário e
    o banco não garantiria a ordem entre elas — na vida real os horários diferem.
    """

    def __init__(self, inicio: datetime) -> None:
        self.agora = inicio

    def __call__(self) -> datetime:
        return self.agora

    def avancar(self, minutos: int = 1) -> None:
        self.agora += timedelta(minutes=minutos)
