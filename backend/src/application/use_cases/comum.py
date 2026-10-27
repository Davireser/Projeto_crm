from uuid import UUID

from application.exceptions import ClienteNaoEncontrado, OrcamentoNaoEncontrado
from domain.entities.cliente import Cliente
from domain.entities.orcamento import Orcamento
from domain.repositories.cliente_repository import ClienteRepository
from domain.repositories.orcamento_repository import OrcamentoRepository


def obter_orcamento(orcamentos: OrcamentoRepository, orcamento_id: UUID) -> Orcamento:
    orcamento = orcamentos.buscar_por_id(orcamento_id)
    if orcamento is None:
        raise OrcamentoNaoEncontrado(orcamento_id)
    return orcamento


def obter_cliente(clientes: ClienteRepository, cliente_id: UUID) -> Cliente:
    cliente = clientes.buscar_por_id(cliente_id)
    if cliente is None:
        raise ClienteNaoEncontrado(cliente_id)
    return cliente
