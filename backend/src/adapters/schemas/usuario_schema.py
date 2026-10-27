from typing import Literal, Self
from uuid import UUID

from adapters.schemas.base import Esquema, InstanteUTC, exemplo
from application.use_cases.gerenciar_usuarios import DadosEdicaoUsuario, DadosNovoUsuario
from domain.entities.usuario import Perfil, Usuario


class LoginEntrada(Esquema):
    model_config = exemplo({"email": "seu@email.com", "senha": "sua-senha"})

    email: str
    senha: str


class UsuarioSaida(Esquema):
    """Dados públicos do usuário — o hash da senha nunca sai da API."""

    id: UUID
    nome: str
    email: str
    perfil: Perfil
    ativo: bool

    @classmethod
    def de(cls, usuario: Usuario) -> Self:
        return cls(
            id=usuario.id,
            nome=usuario.nome,
            email=usuario.email.endereco,
            perfil=usuario.perfil,
            ativo=usuario.ativo,
        )


class TokenSaida(Esquema):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expira_em: InstanteUTC
    usuario: UsuarioSaida


class NovoUsuarioEntrada(Esquema):
    model_config = exemplo(
        {
            "nome": "Joana Lima",
            "email": "joana@empresa.com",
            "senha": "senha-forte-123",
            "perfil": "USUARIO",
        }
    )

    nome: str
    email: str
    senha: str
    perfil: Perfil = Perfil.USUARIO

    def para_dados(self) -> DadosNovoUsuario:
        return DadosNovoUsuario(self.nome, self.email, self.senha, self.perfil)


class EdicaoUsuarioEntrada(Esquema):
    """Só os campos enviados são alterados."""

    model_config = exemplo({"nome": "Joana Silva Lima"})

    nome: str | None = None
    email: str | None = None
    ativo: bool | None = None
    perfil: Perfil | None = None

    def para_dados(self) -> DadosEdicaoUsuario:
        return DadosEdicaoUsuario(self.nome, self.email, self.ativo, self.perfil)
