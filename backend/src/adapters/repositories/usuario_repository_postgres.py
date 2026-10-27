from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from domain.entities.usuario import Administrador, Perfil, Usuario
from domain.repositories.usuario_repository import UsuarioRepository
from domain.value_objects.email import Email
from infra.db.models import UsuarioModel


class UsuarioRepositoryPostgres(UsuarioRepository):
    """Usuario e Administrador na mesma tabela, distinguidos pela coluna `perfil`."""

    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def salvar(self, usuario: Usuario) -> None:
        model = self._sessao.get(UsuarioModel, usuario.id)
        if model is None:
            model = UsuarioModel(id=usuario.id)
            self._sessao.add(model)

        model.nome = usuario.nome
        model.email = usuario.email.endereco
        model.senha_hash = usuario.senha_hash
        model.perfil = usuario.perfil.value
        model.ativo = usuario.ativo
        self._sessao.flush()

    def buscar_por_id(self, usuario_id: UUID) -> Usuario | None:
        model = self._sessao.get(UsuarioModel, usuario_id)
        return _para_entidade(model) if model else None

    def buscar_por_email(self, email: Email) -> Usuario | None:
        model = self._sessao.scalar(
            select(UsuarioModel).where(UsuarioModel.email == email.endereco)
        )
        return _para_entidade(model) if model else None

    def listar_todos(self) -> list[Usuario]:
        consulta = select(UsuarioModel).order_by(UsuarioModel.nome)
        return [_para_entidade(m) for m in self._sessao.scalars(consulta)]


def _para_entidade(model: UsuarioModel) -> Usuario:
    classe = Administrador if model.perfil == Perfil.ADMINISTRADOR.value else Usuario
    return classe(
        id=model.id,
        nome=model.nome,
        email=Email(model.email),
        senha_hash=model.senha_hash,
        ativo=model.ativo,
    )
