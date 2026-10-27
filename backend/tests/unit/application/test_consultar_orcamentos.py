"""UC07 — Consultar Painel Kanban (RF05). Projeção enxuta por card (RNF01)."""

from collections.abc import Callable
from datetime import date
from decimal import Decimal

import pytest

from adapters.repositories.em_memoria import (
    ClienteRepositoryEmMemoria,
    OrcamentoRepositoryEmMemoria,
)
from application.relogio import Relogio
from application.use_cases.consultar_orcamentos import ConsultarOrcamentosUseCase
from application.use_cases.definir_valor import DefinirValorUseCase
from application.use_cases.mover_estagio import MoverEstagioUseCase
from application.use_cases.registrar_interacao import RegistrarInteracaoUseCase
from application.use_cases.registrar_novo_contato import ContatoRegistrado
from domain.value_objects.estagio_atendimento import EstagioAtendimento
from domain.value_objects.tipo_interacao import TipoInteracao

pytestmark = pytest.mark.unit

E = EstagioAtendimento


@pytest.fixture
def use_case(
    orcamentos: OrcamentoRepositoryEmMemoria, clientes: ClienteRepositoryEmMemoria
) -> ConsultarOrcamentosUseCase:
    return ConsultarOrcamentosUseCase(orcamentos, clientes)


def test_painel_vazio_tem_as_cinco_colunas(use_case: ConsultarOrcamentosUseCase) -> None:
    painel = use_case.executar()

    assert list(painel) == list(E)
    assert all(cards == [] for cards in painel.values())


def test_cada_orcamento_aparece_na_coluna_do_seu_estagio(
    use_case: ConsultarOrcamentosUseCase,
    orcamentos: OrcamentoRepositoryEmMemoria,
    relogio: Relogio,
    novo_contato: Callable[..., ContatoRegistrado],
) -> None:
    maria = novo_contato(nome="Maria")
    joao = novo_contato(nome="João", email="joao@x.com")
    MoverEstagioUseCase(orcamentos, relogio).executar(joao.orcamento.id, E.EM_NEGOCIACAO)

    painel = use_case.executar()

    assert [c.cliente_nome for c in painel[E.NOVO_CONTATO]] == ["Maria"]
    assert [c.cliente_nome for c in painel[E.EM_NEGOCIACAO]] == ["João"]
    assert painel[E.NOVO_CONTATO][0].id == maria.orcamento.id


def test_card_traz_a_projecao_enxuta(
    use_case: ConsultarOrcamentosUseCase,
    orcamentos: OrcamentoRepositoryEmMemoria,
    relogio: Relogio,
    novo_contato: Callable[..., ContatoRegistrado],
) -> None:
    contato = novo_contato()
    orcamento_id = contato.orcamento.id
    DefinirValorUseCase(orcamentos).executar(orcamento_id, Decimal("4200"))
    registrar = RegistrarInteracaoUseCase(orcamentos, relogio)
    registrar.executar(orcamento_id, TipoInteracao.MENSAGEM, "Oi")
    registrar.executar(orcamento_id, TipoInteracao.LIGACAO, "Retorno")

    card = use_case.executar()[E.NOVO_CONTATO][0]

    assert card.id == orcamento_id
    assert card.cliente_id == contato.cliente.id
    assert card.cliente_nome == "Maria Souza"
    assert card.estagio is E.NOVO_CONTATO
    assert card.valor == Decimal("4200.00")
    assert card.data_abertura == date(2026, 9, 15)
    assert card.qtd_interacoes == 2


def test_cliente_com_varios_orcamentos_aparece_em_varios_cards(
    use_case: ConsultarOrcamentosUseCase,
    orcamentos: OrcamentoRepositoryEmMemoria,
    novo_contato: Callable[..., ContatoRegistrado],
) -> None:
    contato = novo_contato()
    segundo = contato.cliente.abrir_orcamento(hoje=date(2026, 9, 20))
    orcamentos.salvar(segundo)

    cards = use_case.executar()[E.NOVO_CONTATO]

    assert [c.id for c in cards] == [contato.orcamento.id, segundo.id]
    assert {c.cliente_nome for c in cards} == {"Maria Souza"}
