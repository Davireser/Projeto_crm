from uuid import UUID

from application.relogio import Relogio
from application.use_cases.comum import obter_cliente
from domain.entities.orcamento import Orcamento
from domain.repositories.cliente_repository import ClienteRepository
from domain.repositories.orcamento_repository import OrcamentoRepository


class ReabrirAtendimentoUseCase:
    """Cliente perdido volta ao funil: abre um novo Orçamento, o antigo fica no histórico."""

    def __init__(
        self, clientes: ClienteRepository, orcamentos: OrcamentoRepository, relogio: Relogio
    ) -> None:
        self._clientes = clientes
        self._orcamentos = orcamentos
        self._relogio = relogio

    def executar(self, cliente_id: UUID) -> Orcamento:
        cliente = obter_cliente(self._clientes, cliente_id)
        orcamento = cliente.reabrir_atendimento(
            self._orcamentos.listar_por_cliente(cliente_id), hoje=self._relogio().date()
        )
        self._orcamentos.salvar(orcamento)
        return orcamento
