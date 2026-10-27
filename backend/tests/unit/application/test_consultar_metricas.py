"""UC08 — Consultar Métricas do Funil (RF06, RN07). Item 3 do plano de TDD: cálculo puro."""

from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from adapters.repositories.em_memoria import OrcamentoRepositoryEmMemoria
from application.use_cases.consultar_metricas import (
    ConsultarMetricasUseCase,
    MetricasFunil,
    calcular_metricas,
)
from domain.entities.orcamento import Orcamento
from domain.value_objects.estagio_atendimento import EstagioAtendimento
from domain.value_objects.valor_orcado import ValorOrcado

pytestmark = pytest.mark.unit

E = EstagioAtendimento


def orcamentos_em(*estagios: EstagioAtendimento) -> list[Orcamento]:
    return [
        Orcamento(
            id=uuid4(),
            cliente_id=uuid4(),
            estagio=estagio,
            valor=ValorOrcado(Decimal("100")),
            data_abertura=date(2026, 9, 1),
        )
        for estagio in estagios
    ]


def test_funil_vazio_tem_taxa_indefinida() -> None:
    assert calcular_metricas([]) == MetricasFunil(
        em_aberto=0, fechados=0, perdidos=0, taxa_fechamento=None
    )


def test_conta_abertos_e_calcula_taxa_sobre_os_concluidos() -> None:
    lista = orcamentos_em(
        E.NOVO_CONTATO,
        E.EM_NEGOCIACAO,
        E.ORCAMENTO_ENVIADO,
        E.FECHADO,
        E.FECHADO,
        E.FECHADO,
        E.PERDIDO,
    )

    assert calcular_metricas(lista) == MetricasFunil(
        em_aberto=3, fechados=3, perdidos=1, taxa_fechamento=Decimal("75.00")
    )


def test_so_orcamentos_abertos_tem_taxa_indefinida_e_nao_zero() -> None:
    metricas = calcular_metricas(orcamentos_em(E.NOVO_CONTATO, E.EM_NEGOCIACAO))

    assert metricas.em_aberto == 2
    assert metricas.taxa_fechamento is None


@pytest.mark.parametrize(
    ("estagios", "taxa"),
    [
        ((E.PERDIDO, E.PERDIDO), Decimal("0.00")),
        ((E.FECHADO,), Decimal("100.00")),
        ((E.FECHADO, E.PERDIDO, E.PERDIDO), Decimal("33.33")),
        ((E.FECHADO, E.FECHADO, E.PERDIDO), Decimal("66.67")),
    ],
)
def test_taxa_em_percentual_com_duas_casas(
    estagios: tuple[EstagioAtendimento, ...], taxa: Decimal
) -> None:
    assert calcular_metricas(orcamentos_em(*estagios)).taxa_fechamento == taxa


def test_use_case_le_os_orcamentos_do_repositorio() -> None:
    repositorio = OrcamentoRepositoryEmMemoria()
    for orcamento in orcamentos_em(E.NOVO_CONTATO, E.FECHADO, E.PERDIDO):
        repositorio.salvar(orcamento)

    metricas = ConsultarMetricasUseCase(repositorio).executar()

    assert metricas == MetricasFunil(
        em_aberto=1, fechados=1, perdidos=1, taxa_fechamento=Decimal("50.00")
    )
