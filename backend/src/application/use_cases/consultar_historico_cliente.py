from dataclasses import dataclass
from uuid import UUID

from application.use_cases.comum import obter_cliente
from domain.entities.interacao import Interacao
from domain.repositories.cliente_repository import ClienteRepository
from domain.repositories.orcamento_repository import OrcamentoRepository


@dataclass(frozen=True)
class ItemHistorico:
    """Uma interação na linha do tempo, com o orçamento a que pertence (para agrupar na tela)."""

    orcamento_id: UUID
    interacao: Interacao


class ConsultarHistoricoClienteUseCase:
    """UC09: interações de todos os orçamentos do cliente, em ordem cronológica (RF07, RN08)."""

    def __init__(self, clientes: ClienteRepository, orcamentos: OrcamentoRepository) -> None:
        self._clientes = clientes
        self._orcamentos = orcamentos

    def executar(self, cliente_id: UUID) -> list[ItemHistorico]:
        obter_cliente(self._clientes, cliente_id)
        itens = [
            ItemHistorico(orcamento_id=orcamento.id, interacao=interacao)
            for orcamento in self._orcamentos.listar_por_cliente(cliente_id)
            for interacao in orcamento.interacoes
        ]
        return sorted(itens, key=lambda item: item.interacao.data_hora)
