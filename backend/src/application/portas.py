"""Portas (interfaces) de serviços externos usados pelos casos de uso."""

from typing import Protocol


class HashDeSenha(Protocol):
    """Gera e confere hashes de senha. A senha em texto puro nunca é guardada (RNF07).

    Implementação real: infra/security.py (scrypt). Nos testes de unidade, um falso.
    """

    def gerar(self, senha: str) -> str: ...

    def confere(self, senha: str, hash_guardado: str) -> bool: ...
