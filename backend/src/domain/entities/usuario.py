from dataclasses import dataclass, replace
from enum import StrEnum
from typing import ClassVar
from uuid import UUID

from domain.exceptions import FormatoInvalido, OperacaoNaoPermitida
from domain.value_objects.email import Email


class Perfil(StrEnum):
    USUARIO = "USUARIO"
    ADMINISTRADOR = "ADMINISTRADOR"


@dataclass(frozen=True, kw_only=True)
class Usuario:
    """Operador do sistema. Periférico ao funil — não participa do agregado Orçamento.

    Imutável: alterações devolvem um novo Usuario.
    """

    perfil: ClassVar[Perfil] = Perfil.USUARIO

    id: UUID
    nome: str
    email: Email
    senha_hash: str
    ativo: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "nome", _nome_valido(self.nome))

    def atualizar_cadastro(self, *, nome: str, email: Email) -> "Usuario":
        return replace(self, nome=nome, email=email)


@dataclass(frozen=True, kw_only=True)
class Administrador(Usuario):
    """Usuário com permissão para gerenciar outros usuários (RF10).

    Persistido na mesma tabela de `Usuario`, distinguido pela coluna `perfil`.
    """

    perfil: ClassVar[Perfil] = Perfil.ADMINISTRADOR

    def desativar_usuario(self, usuario: Usuario) -> Usuario:
        if usuario.id == self.id:
            raise OperacaoNaoPermitida(
                "Um administrador não pode desativar a própria conta.", campo="ativo"
            )
        return replace(usuario, ativo=False)

    def ativar_usuario(self, usuario: Usuario) -> Usuario:
        return replace(usuario, ativo=True)

    def definir_perfil(self, usuario: Usuario, perfil: Perfil) -> Usuario:
        """Devolve o mesmo usuário (mesmo id e dados) com o novo perfil.

        O próprio administrador não pode mudar o seu perfil — evita que o sistema
        fique sem ninguém capaz de gerenciar usuários.
        """
        if usuario.id == self.id:
            raise OperacaoNaoPermitida(
                "Um administrador não pode alterar o próprio perfil.", campo="perfil"
            )
        classe = Administrador if perfil is Perfil.ADMINISTRADOR else Usuario
        return classe(
            id=usuario.id,
            nome=usuario.nome,
            email=usuario.email,
            senha_hash=usuario.senha_hash,
            ativo=usuario.ativo,
        )


def _nome_valido(nome: str) -> str:
    nome = nome.strip()
    if not nome:
        raise FormatoInvalido("O nome do usuário é obrigatório.", campo="nome")
    return nome
