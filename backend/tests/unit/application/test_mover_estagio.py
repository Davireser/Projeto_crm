"""UC03 — Mover Estágio do Orçamento (RF02, RF03, RNF04). Item 5 do plano de TDD."""

from collections.abc import Callable
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from adapters.repositories.em_memoria import OrcamentoRepositoryEmMemoria
from application.exceptions import OrcamentoNaoEncontrado
from application.relogio import Relogio
from application.use_cases.definir_valor import DefinirValorUseCase
from application.use_cases.mover_estagio import MoverEstagioUseCase
from application.use_cases.registrar_novo_contato import ContatoRegistrado
from domain.exceptions import TransicaoInvalida
from domain.value_objects.estagio_atendimento import EstagioAtendimento

pytestmark = pytest.mark.unit

E = EstagioAtendimento


@pytest.fixture
def use_case(orcamentos: OrcamentoRepositoryEmMemoria, relogio: Relogio) -> MoverEstagioUseCase:
    return MoverEstagioUseCase(orcamentos, relogio)


def test_move_e_persiste_o_novo_estagio(
    use_case: MoverEstagioUseCase,
    orcamentos: OrcamentoRepositoryEmMemoria,
    novo_contato: Callable[..., ContatoRegistrado],
) -> None:
    orcamento_id = novo_contato().orcamento.id

    resultado = use_case.executar(orcamento_id, E.EM_NEGOCIACAO)

    assert resultado.estagio is E.EM_NEGOCIACAO
    salvo = orcamentos.buscar_por_id(orcamento_id)
    assert salvo is not None
    assert salvo.estagio is E.EM_NEGOCIACAO


def test_transicao_invalida_propaga_erro_sem_salvar(
    use_case: MoverEstagioUseCase,
    orcamentos: OrcamentoRepositoryEmMemoria,
    novo_contato: Callable[..., ContatoRegistrado],
) -> None:
    orcamento_id = novo_contato().orcamento.id
    salvamentos_antes = orcamentos.salvamentos

    with pytest.raises(TransicaoInvalida) as erro:
        use_case.executar(orcamento_id, E.FECHADO)

    assert erro.value.campo == "estagio"
    assert orcamentos.salvamentos == salvamentos_antes
    salvo = orcamentos.buscar_por_id(orcamento_id)
    assert salvo is not None
    assert salvo.estagio is E.NOVO_CONTATO


def test_enviar_sem_valor_propaga_erro_sem_salvar(
    use_case: MoverEstagioUseCase,
    orcamentos: OrcamentoRepositoryEmMemoria,
    novo_contato: Callable[..., ContatoRegistrado],
) -> None:
    orcamento_id = novo_contato().orcamento.id
    use_case.executar(orcamento_id, E.EM_NEGOCIACAO)
    salvamentos_antes = orcamentos.salvamentos

    with pytest.raises(TransicaoInvalida) as erro:
        use_case.executar(orcamento_id, E.ORCAMENTO_ENVIADO)

    assert erro.value.campo == "valor"
    assert orcamentos.salvamentos == salvamentos_antes


def test_fechar_usa_a_data_do_relogio(
    use_case: MoverEstagioUseCase,
    orcamentos: OrcamentoRepositoryEmMemoria,
    novo_contato: Callable[..., ContatoRegistrado],
    agora: datetime,
) -> None:
    orcamento_id = novo_contato().orcamento.id
    DefinirValorUseCase(orcamentos).executar(orcamento_id, Decimal("4200.00"))
    for estagio in (E.EM_NEGOCIACAO, E.ORCAMENTO_ENVIADO, E.FECHADO):
        use_case.executar(orcamento_id, estagio)

    salvo = orcamentos.buscar_por_id(orcamento_id)
    assert salvo is not None
    assert salvo.estagio is E.FECHADO
    assert salvo.data_fechamento == agora.date()


def test_orcamento_inexistente(use_case: MoverEstagioUseCase) -> None:
    with pytest.raises(OrcamentoNaoEncontrado):
        use_case.executar(uuid4(), E.EM_NEGOCIACAO)
