import re
from dataclasses import dataclass

from domain.exceptions import FormatoInvalido

_CARACTERES_DE_MASCARA = re.compile(r"[\s().\-+]")
# DDD: dois dígitos de 1 a 9. Fixo: 8 dígitos. Celular: 9 dígitos começando com 9.
_TELEFONE_BRASILEIRO = re.compile(r"[1-9]{2}(?:[2-8]\d{7}|9\d{8})")


@dataclass(frozen=True)
class Telefone:
    """Telefone brasileiro com DDD, armazenado somente com dígitos (RN04)."""

    numero: str

    def __post_init__(self) -> None:
        digitos = _CARACTERES_DE_MASCARA.sub("", self.numero)
        if not _TELEFONE_BRASILEIRO.fullmatch(digitos):
            raise FormatoInvalido(
                f"Telefone inválido: '{self.numero}'. Informe DDD + número, "
                "com 10 dígitos (fixo) ou 11 dígitos (celular).",
                campo="telefone",
            )
        object.__setattr__(self, "numero", digitos)
