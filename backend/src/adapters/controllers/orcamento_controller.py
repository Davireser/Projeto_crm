from uuid import UUID

from fastapi import APIRouter

from adapters.controllers.dependencias import Clientes, Orcamentos, RelogioDaApp
from adapters.schemas.orcamento_schema import (
    CardSaida,
    DefinirValorEntrada,
    MoverEstagioEntrada,
    OrcamentoSaida,
    TransicoesSaida,
)
from application.use_cases.consultar_orcamentos import ConsultarOrcamentosUseCase
from application.use_cases.definir_valor import DefinirValorUseCase
from application.use_cases.mover_estagio import MoverEstagioUseCase
from domain.value_objects.estagio_atendimento import EstagioAtendimento

router = APIRouter(prefix="/orcamentos", tags=["orcamentos"])


@router.get("")
def consultar_painel(
    orcamentos: Orcamentos, clientes: Clientes
) -> dict[EstagioAtendimento, list[CardSaida]]:
    """UC07: orçamentos agrupados por estágio, uma coluna por estágio (RF05)."""
    painel = ConsultarOrcamentosUseCase(orcamentos, clientes).executar()
    return {estagio: [CardSaida.de(card) for card in cards] for estagio, cards in painel.items()}


@router.get("/transicoes")
def consultar_transicoes() -> TransicoesSaida:
    """Mapa de transições permitidas (RN01): o Kanban usa, nunca reimplementa a regra."""
    return TransicoesSaida.do_dominio()


@router.patch("/{orcamento_id}/estagio")
def mover_estagio(
    orcamento_id: UUID,
    entrada: MoverEstagioEntrada,
    orcamentos: Orcamentos,
    relogio: RelogioDaApp,
) -> OrcamentoSaida:
    """UC03: o domínio decide; transição inválida vira 422 TransicaoInvalida."""
    orcamento = MoverEstagioUseCase(orcamentos, relogio).executar(orcamento_id, entrada.estagio)
    return OrcamentoSaida.de(orcamento)


@router.patch("/{orcamento_id}/valor")
def definir_valor(
    orcamento_id: UUID, entrada: DefinirValorEntrada, orcamentos: Orcamentos
) -> OrcamentoSaida:
    """UC05: define o valor, liberando as transições guardadas (RF03)."""
    orcamento = DefinirValorUseCase(orcamentos).executar(orcamento_id, entrada.valor)
    return OrcamentoSaida.de(orcamento)
