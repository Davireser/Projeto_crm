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
        nome = nome.strip()
        if not nome:
            raise FormatoInvalido("O nome do usuário é obrigatório.", campo="nome")

        self._id = id
        self._nome = nome
        self._email = email
        self._senha_hash = senha_hash
        self._ativo = ativo

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
