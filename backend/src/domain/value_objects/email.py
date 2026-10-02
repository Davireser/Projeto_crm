import re
from dataclasses import dataclass

from domain.exceptions import FormatoInvalido

_EMAIL = re.compile(r"[a-z0-9._%+\-]+@[a-z0-9\-]+(?:\.[a-z0-9\-]+)*\.[a-z]{2,}")


@dataclass(frozen=True)
class Email:
    """Endereço `local@dominio.tld`, normalizado para minúsculas (RN05)."""

    endereco: str

    def __post_init__(self) -> None:
        normalizado = self.endereco.strip().lower()
        if not _EMAIL.fullmatch(normalizado):
            raise FormatoInvalido(f"E-mail inválido: '{self.endereco}'.", campo="email")
        object.__setattr__(self, "endereco", normalizado)
