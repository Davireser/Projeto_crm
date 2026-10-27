from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from domain.repositories.cliente_repository import ClienteRepository
from domain.repositories.orcamento_repository import OrcamentoRepository
from domain.value_objects.estagio_atendimento import EstagioAtendimento


@dataclass(frozen=True)
class CardOrcamento:
    """Projeção enxuta de um card do Kanban — sem as interações em si (RNF01)."""

    id: UUID
    cliente_id: UUID
    cliente_nome: str
    estagio: EstagioAtendimento
    valor: Decimal | None
    data_abertura: date
    qtd_interacoes: int


type Painel = dict[EstagioAtendimento, list[CardOrcamento]]


class ConsultarOrcamentosUseCase:
    """UC07: orçamentos agrupados por estágio, uma coluna por estágio (RF05).

    Todas as cinco colunas aparecem, mesmo vazias. Dentro da coluna, os cards
    vêm do mais antigo para o mais recente (quem espera há mais tempo primeiro).
    """

    def __init__(self, orcamentos: OrcamentoRepository, clientes: ClienteRepository) -> None:
        self._orcamentos = orcamentos
        self._clientes = clientes

    def executar(self) -> Painel:
        orcamentos = sorted(self._orcamentos.listar_todos(), key=lambda o: o.data_abertura)
        nomes = {
            c.id: c.nome for c in self._clientes.listar_por_ids({o.cliente_id for o in orcamentos})
        }

        painel: Painel = {estagio: [] for estagio in EstagioAtendimento}
        for orcamento in orcamentos:
            painel[orcamento.estagio].append(
                CardOrcamento(
                    id=orcamento.id,
                    cliente_id=orcamento.cliente_id,
                    cliente_nome=nomes[orcamento.cliente_id],
                    estagio=orcamento.estagio,
                    valor=orcamento.valor.valor if orcamento.valor else None,
                    data_abertura=orcamento.data_abertura,
                    qtd_interacoes=len(orcamento.interacoes),
                )
            )
        return painel
