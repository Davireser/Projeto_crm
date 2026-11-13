"""Reabrir atendimento: cliente perdido volta ao funil com um novo orçamento."""

from collections.abc import Callable
from datetime import date
from uuid import uuid4

import pytest

from adapters.repositories.em_memoria import (
    ClienteRepositoryEmMemoria,
    OrcamentoRepositoryEmMemoria,
)
from application.exceptions import ClienteNaoEncontrado
from application.relogio import Relogio
from application.use_cases.reabrir_atendimento import ReabrirAtendimentoUseCase
from application.use_cases.registrar_novo_contato import ContatoRegistrado
from domain.exceptions import OperacaoNaoPermitida
from domain.value_objects.estagio_atendimento import EstagioAtendimento as E

pytestmark = pytest.mark.unit


@pytest.fixture
def use_case(
    clientes: ClienteRepositoryEmMemoria,
    orcamentos: OrcamentoRepositoryEmMemoria,
    relogio: Relogio,
) -> ReabrirAtendimentoUseCase:
    return ReabrirAtendimentoUseCase(clientes, orcamentos, relogio)


def test_cliente_perdido_ganha_novo_orcamento_em_novo_contato(
    use_case: ReabrirAtendimentoUseCase,
    orcamentos: OrcamentoRepositoryEmMemoria,
    novo_contato: Callable[..., ContatoRegistrado],
) -> None:
    contato = novo_contato()
    orcamentos.salvar(contato.orcamento.mover_estagio(E.PERDIDO, date(2026, 9, 10)))

    novo = use_case.executar(contato.cliente.id)

    assert novo.estagio is E.NOVO_CONTATO
    assert novo.data_abertura == date(2026, 9, 15)
    estagios = {o.id: o.estagio for o in orcamentos.listar_por_cliente(contato.cliente.id)}
    assert estagios == {contato.orcamento.id: E.PERDIDO, novo.id: E.NOVO_CONTATO}


def test_nao_reabre_quem_ainda_tem_orcamento_em_aberto(
    use_case: ReabrirAtendimentoUseCase,
    orcamentos: OrcamentoRepositoryEmMemoria,
    novo_contato: Callable[..., ContatoRegistrado],
) -> None:
    contato = novo_contato()

    with pytest.raises(OperacaoNaoPermitida):
        use_case.executar(contato.cliente.id)
    assert len(orcamentos.listar_por_cliente(contato.cliente.id)) == 1


def test_cliente_inexistente(use_case: ReabrirAtendimentoUseCase) -> None:
    with pytest.raises(ClienteNaoEncontrado):
        use_case.executar(uuid4())
