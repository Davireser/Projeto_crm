from decimal import Decimal
from uuid import UUID

from application.use_cases.comum import obter_orcamento
from domain.entities.orcamento import Orcamento
from domain.repositories.orcamento_repository import OrcamentoRepository
from domain.value_objects.valor_orcado import ValorOrcado


class DefinirValorUseCase:
    """UC05: define o valor do orçamento, liberando as transições guardadas (RF03)."""

    def __init__(self, orcamentos: OrcamentoRepository) -> None:
        self._orcamentos = orcamentos

    def executar(self, orcamento_id: UUID, valor: Decimal) -> Orcamento:
        orcamento = obter_orcamento(self._orcamentos, orcamento_id)
        orcamento.definir_valor(ValorOrcado(valor))
        self._orcamentos.salvar(orcamento)
        return orcamento
