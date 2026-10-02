"""Mapa de transições do funil (RN01) — espelha docs/arquitetura/10-diagrama-estados.md."""

import pytest

from domain.value_objects.estagio_atendimento import TRANSICOES_PERMITIDAS, EstagioAtendimento

pytestmark = pytest.mark.unit

E = EstagioAtendimento


def test_funil_tem_exatamente_cinco_estagios() -> None:
    assert [e.value for e in E] == [
        "NOVO_CONTATO",
        "EM_NEGOCIACAO",
        "ORCAMENTO_ENVIADO",
        "FECHADO",
        "PERDIDO",
    ]


def test_mapa_de_transicoes_reflete_o_diagrama_de_estados() -> None:
    assert {
        E.NOVO_CONTATO: frozenset({E.EM_NEGOCIACAO, E.PERDIDO}),
        E.EM_NEGOCIACAO: frozenset({E.ORCAMENTO_ENVIADO, E.PERDIDO}),
        E.ORCAMENTO_ENVIADO: frozenset({E.FECHADO, E.PERDIDO}),
        E.FECHADO: frozenset(),
        E.PERDIDO: frozenset(),
    } == TRANSICOES_PERMITIDAS


@pytest.mark.parametrize(
    ("estagio", "terminal"),
    [
        (E.NOVO_CONTATO, False),
        (E.EM_NEGOCIACAO, False),
        (E.ORCAMENTO_ENVIADO, False),
        (E.FECHADO, True),
        (E.PERDIDO, True),
    ],
)
def test_somente_fechado_e_perdido_sao_terminais(
    estagio: EstagioAtendimento, terminal: bool
) -> None:
    assert estagio.eh_terminal() is terminal


def test_somente_enviado_e_fechado_exigem_valor() -> None:
    assert {e for e in E if e.exige_valor()} == {E.ORCAMENTO_ENVIADO, E.FECHADO}
