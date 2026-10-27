from dataclasses import dataclass
from uuid import UUID

from application.use_cases.comum import obter_cliente
from domain.entities.cliente import Cliente
from domain.entities.orcamento import Orcamento
from domain.repositories.cliente_repository import ClienteRepository
from domain.repositories.orcamento_repository import OrcamentoRepository


@dataclass(frozen=True)
class ClienteComOrcamentos:
    cliente: Cliente
    orcamentos: list[Orcamento]


class ConsultarClienteUseCase:
    """UC09 (detalhe): o cliente com todos os seus orçamentos, por data de abertura (RF08)."""

    def __init__(self, clientes: ClienteRepository, orcamentos: OrcamentoRepository) -> None:
        self._clientes = clientes
        self._orcamentos = orcamentos

    def executar(self, cliente_id: UUID) -> ClienteComOrcamentos:
        cliente = obter_cliente(self._clientes, cliente_id)
        orcamentos = sorted(
            self._orcamentos.listar_por_cliente(cliente_id), key=lambda o: o.data_abertura
        )
        return ClienteComOrcamentos(cliente=cliente, orcamentos=orcamentos)
