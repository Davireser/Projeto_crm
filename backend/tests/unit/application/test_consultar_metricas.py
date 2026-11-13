"""UC08 — Consultar Métricas do Funil (RF06, RN07). Item 3 do plano de TDD: cálculo puro."""

from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from adapters.repositories.em_memoria import OrcamentoRepositoryEmMemoria
from application.use_cases.consultar_metricas import (
    ConsultarMetricasUseCase,
    TotalDoEstagio,
    calcular_metricas,
)
from domain.entities.orcamento import Orcamento
from domain.value_objects.estagio_atendimento import EstagioAtendimento
from domain.value_objects.valor_orcado import ValorOrcado

pytestmark = pytest.mark.unit

E = EstagioAtendimento


def orcamento(estagio: EstagioAtendimento, valor: str | None = "100") -> Orcamento:
    return Orcamento(
        id=uuid4(),
        cliente_id=uuid4(),
        estagio=estagio,
        valor=ValorOrcado(Decimal(valor)) if valor else None,
        data_abertura=date(2026, 9, 1),
    )


def orcamentos_em(*estagios: EstagioAtendimento) -> list[Orcamento]:
    return [orcamento(estagio) for estagio in estagios]


def test_funil_vazio_tem_taxa_indefinida() -> None:
    metricas = calcular_metricas([])

    assert (metricas.em_aberto, metricas.fechados, metricas.perdidos) == (0, 0, 0)
    assert metricas.taxa_fechamento is None


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

    metricas = calcular_metricas(lista)

    assert (metricas.em_aberto, metricas.fechados, metricas.perdidos) == (3, 3, 1)
    assert metricas.taxa_fechamento == Decimal("75.00")


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


def test_soma_o_dinheiro_de_cada_estagio_na_ordem_do_funil() -> None:
    lista = [
        orcamento(E.NOVO_CONTATO, valor=None),
        orcamento(E.EM_NEGOCIACAO, "1500.50"),
        orcamento(E.EM_NEGOCIACAO, "499.50"),
        orcamento(E.EM_NEGOCIACAO, valor=None),
        orcamento(E.FECHADO, "12500"),
    ]

    assert calcular_metricas(lista).por_estagio == (
        TotalDoEstagio(E.NOVO_CONTATO, quantidade=1, valor_total=Decimal("0.00"), sem_valor=1),
        TotalDoEstagio(E.EM_NEGOCIACAO, quantidade=3, valor_total=Decimal("2000.00"), sem_valor=1),
        TotalDoEstagio(E.ORCAMENTO_ENVIADO, quantidade=0, valor_total=Decimal("0.00"), sem_valor=0),
        TotalDoEstagio(E.FECHADO, quantidade=1, valor_total=Decimal("12500.00"), sem_valor=0),
        TotalDoEstagio(E.PERDIDO, quantidade=0, valor_total=Decimal("0.00"), sem_valor=0),
    )


def test_use_case_le_os_orcamentos_do_repositorio() -> None:
    repositorio = OrcamentoRepositoryEmMemoria()
    for item in orcamentos_em(E.NOVO_CONTATO, E.FECHADO, E.PERDIDO):
        repositorio.salvar(item)

    metricas = ConsultarMetricasUseCase(repositorio).executar()

    assert (metricas.em_aberto, metricas.fechados, metricas.perdidos) == (1, 1, 1)
    assert metricas.taxa_fechamento == Decimal("50.00")
    assert [t.valor_total for t in metricas.por_estagio] == [
        Decimal("100.00"),
        Decimal("0.00"),
        Decimal("0.00"),
        Decimal("100.00"),
        Decimal("100.00"),
    ]
