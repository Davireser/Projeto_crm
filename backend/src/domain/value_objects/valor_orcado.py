from dataclasses import dataclass
from decimal import Decimal

from domain.exceptions import ValorInvalido

_DUAS_CASAS = Decimal("0.01")


@dataclass(frozen=True)
class ValorOrcado:
    """Valor em BRL, maior que zero, com no máximo duas casas decimais (RN06)."""

    valor: Decimal

    def __post_init__(self) -> None:
        if not self.valor.is_finite() or self.valor <= 0:
            raise ValorInvalido(
                f"Valor orçado deve ser maior que zero; recebido {self.valor}.", campo="valor"
            )
        normalizado = self.valor.quantize(_DUAS_CASAS)
        if normalizado != self.valor:
            raise ValorInvalido(
                f"Valor orçado aceita no máximo duas casas decimais; recebido {self.valor}.",
                campo="valor",
            )
        object.__setattr__(self, "valor", normalizado)
