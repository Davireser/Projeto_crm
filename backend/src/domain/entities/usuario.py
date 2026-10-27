from enum import StrEnum
from uuid import UUID

from domain.exceptions import FormatoInvalido, OperacaoNaoPermitida
from domain.value_objects.email import Email


class Perfil(StrEnum):
    USUARIO = "USUARIO"
    ADMINISTRADOR = "ADMINISTRADOR"


class Usuario:
    """Operador do sistema. Periférico ao funil — não participa do agregado Orçamento."""

    perfil: Perfil = Perfil.USUARIO

    def __init__(
        self, *, id: UUID, nome: str, email: Email, senha_hash: str, ativo: bool = True
    ) -> None:
        self._id = id
        self._nome = _nome_valido(nome)
        self._email = email
        self._senha_hash = senha_hash
        self._ativo = ativo

    def atualizar_cadastro(self, *, nome: str, email: Email) -> None:
        self._nome = _nome_valido(nome)
        self._email = email

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def nome(self) -> str:
        return self._nome

    @property
    def email(self) -> Email:
        return self._email

    @property
    def senha_hash(self) -> str:
        return self._senha_hash

    @property
    def ativo(self) -> bool:
        return self._ativo


class Administrador(Usuario):
    """Usuário com permissão para gerenciar outros usuários (RF10).

    Persistido na mesma tabela de `Usuario`, distinguido pela coluna `perfil`.
    """

    perfil = Perfil.ADMINISTRADOR

    def desativar_usuario(self, usuario: Usuario) -> None:
        if usuario.id == self.id:
            raise OperacaoNaoPermitida(
                "Um administrador não pode desativar a própria conta.", campo="ativo"
            )
        usuario._ativo = False

    def ativar_usuario(self, usuario: Usuario) -> None:
        usuario._ativo = True

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
