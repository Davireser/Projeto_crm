"""Segurança: hash de senha (scrypt) e token de acesso (JWT) — RNF07.

O scrypt vem na biblioteca padrão do Python (hashlib), então não depende de
pacotes compilados como bcrypt/argon2 — que o Smart App Control desta máquina
bloquearia.
"""

import base64
import hashlib
import hmac
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID

import jwt

from application.relogio import Relogio
from domain.entities.usuario import Usuario


def _b64(dados: bytes) -> str:
    return base64.b64encode(dados).decode("ascii")


class HashScrypt:
    """Implementa a porta HashDeSenha. Formato: scrypt$n$r$p$sal$hash (base64).

    Os parâmetros ficam gravados junto do hash, então dá para aumentar o custo
    no futuro sem invalidar as senhas já cadastradas.
    """

    def __init__(self, n: int = 2**14, r: int = 8, p: int = 1) -> None:
        self._n, self._r, self._p = n, r, p

    def gerar(self, senha: str) -> str:
        sal = os.urandom(16)
        derivado = self._derivar(senha, sal, self._n, self._r, self._p)
        return f"scrypt${self._n}${self._r}${self._p}${_b64(sal)}${_b64(derivado)}"

    def confere(self, senha: str, hash_guardado: str) -> bool:
        try:
            algoritmo, n, r, p, sal, esperado = hash_guardado.split("$")
            if algoritmo != "scrypt":
                return False
            obtido = self._derivar(senha, base64.b64decode(sal), int(n), int(r), int(p))
            return hmac.compare_digest(obtido, base64.b64decode(esperado))
        except ValueError:
            return False

    @staticmethod
    def _derivar(senha: str, sal: bytes, n: int, r: int, p: int) -> bytes:
        return hashlib.scrypt(senha.encode("utf-8"), salt=sal, n=n, r=r, p=p, dklen=32)


class TokenInvalido(Exception):
    """Token ausente, mal formado, com assinatura errada ou expirado."""


@dataclass(frozen=True)
class TokenEmitido:
    valor: str
    expira_em: datetime


class EmissorJWT:
    """Emite e lê tokens JWT assinados com HMAC.

    A validade é conferida com o relógio da aplicação (e não com o do sistema),
    para que os testes possam simular a passagem do tempo.
    """

    def __init__(
        self, segredo: str, algoritmo: str, validade_minutos: int, relogio: Relogio
    ) -> None:
        self._segredo = segredo
        self._algoritmo = algoritmo
        self._validade = timedelta(minutes=validade_minutos)
        self._relogio = relogio

    def emitir(self, usuario: Usuario) -> TokenEmitido:
        # O JWT guarda segundos inteiros; a data devolvida à API segue o mesmo valor.
        agora = self._relogio().replace(microsecond=0)
        expira_em = agora + self._validade
        conteudo = {
            "sub": str(usuario.id),
            "perfil": usuario.perfil.value,
            "iat": int(agora.timestamp()),
            "exp": int(expira_em.timestamp()),
        }
        return TokenEmitido(jwt.encode(conteudo, self._segredo, self._algoritmo), expira_em)

    def ler(self, token: str) -> UUID:
        """Devolve o id do usuário dono do token, ou lança TokenInvalido."""
        try:
            conteudo = jwt.decode(
                token,
                self._segredo,
                algorithms=[self._algoritmo],
                options={"verify_exp": False, "require": ["sub", "exp"]},
            )
            if int(conteudo["exp"]) <= int(self._relogio().timestamp()):
                raise TokenInvalido("Token expirado.")
            return UUID(str(conteudo["sub"]))
        except (jwt.PyJWTError, ValueError) as erro:
            raise TokenInvalido(str(erro)) from erro
