from collections.abc import Iterable
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from domain.entities.cliente import Cliente
from domain.repositories.cliente_repository import ClienteRepository
from domain.value_objects.email import Email
from domain.value_objects.telefone import Telefone
from infra.db.models import ClienteModel


class ClienteRepositoryPostgres(ClienteRepository):
    """Persiste o agregado Cliente via SQLAlchemy. Não faz commit."""

    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def salvar(self, cliente: Cliente) -> None:
        model = self._sessao.get(ClienteModel, cliente.id)
        if model is None:
            model = ClienteModel(id=cliente.id)
            self._sessao.add(model)

        model.nome = cliente.nome
        model.telefone = cliente.telefone.numero
        model.email = cliente.email.endereco
        model.empresa = cliente.empresa
        model.tipo_embalagem_interesse = cliente.tipo_embalagem_interesse
        model.criado_em = cliente.criado_em
        self._sessao.flush()

    def buscar_por_id(self, cliente_id: UUID) -> Cliente | None:
        model = self._sessao.get(ClienteModel, cliente_id)
        return _para_entidade(model) if model else None

    def listar_por_ids(self, cliente_ids: Iterable[UUID]) -> list[Cliente]:
        ids = set(cliente_ids)
        if not ids:
            return []
        consulta = select(ClienteModel).where(ClienteModel.id.in_(ids))
        return [_para_entidade(m) for m in self._sessao.scalars(consulta)]


def _para_entidade(model: ClienteModel) -> Cliente:
    # Os dados já foram validados ao entrar; reconstruir os Value Objects
    # garante que um dado corrompido no banco não passe despercebido.
    return Cliente(
        id=model.id,
        nome=model.nome,
        telefone=Telefone(model.telefone),
        email=Email(model.email),
        criado_em=model.criado_em,
        empresa=model.empresa,
        tipo_embalagem_interesse=model.tipo_embalagem_interesse,
    )
