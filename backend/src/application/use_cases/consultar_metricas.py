from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from decimal import Decimal

from domain.entities.orcamento import Orcamento
from domain.repositories.orcamento_repository import OrcamentoRepository
from domain.value_objects.estagio_atendimento import EstagioAtendimento

_DUAS_CASAS = Decimal("0.01")


@dataclass(frozen=True)
class MetricasFunil:
    em_aberto: int
    fechados: int
    perdidos: int
    taxa_fechamento: Decimal | None
    """Percentual de FECHADO sobre (FECHADO + PERDIDO). `None` quando nada foi
    concluído ainda — a interface mostra "—", não zero (RN07)."""


def calcular_metricas(orcamentos: Iterable[Orcamento]) -> MetricasFunil:
    """Cálculo puro das métricas do funil (RN07), sem banco."""
    por_estagio = Counter(o.estagio for o in orcamentos)
    fechados = por_estagio[EstagioAtendimento.FECHADO]
    perdidos = por_estagio[EstagioAtendimento.PERDIDO]
    em_aberto = sum(qtd for estagio, qtd in por_estagio.items() if not estagio.eh_terminal())

    concluidos = fechados + perdidos
    taxa = (Decimal(100 * fechados) / concluidos).quantize(_DUAS_CASAS) if concluidos else None
    return MetricasFunil(
        em_aberto=em_aberto, fechados=fechados, perdidos=perdidos, taxa_fechamento=taxa
    )


class ConsultarMetricasUseCase:
    """UC08: métricas exibidas no topo do painel (RF06)."""

    def __init__(self, orcamentos: OrcamentoRepository) -> None:
        self._orcamentos = orcamentos

    def executar(self) -> MetricasFunil:
        return calcular_metricas(self._orcamentos.listar_todos())
