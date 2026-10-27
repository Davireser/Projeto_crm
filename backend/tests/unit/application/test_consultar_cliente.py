"""UC09 — Consultar Cliente e seu Histórico (RF07, RF08, RN08)."""

from collections.abc import Callable
from datetime import UTC, date, datetime
from uuid import uuid4

import pytest

from adapters.repositories.em_memoria import (
    ClienteRepositoryEmMemoria,
    OrcamentoRepositoryEmMemoria,
)
from application.exceptions import ClienteNaoEncontrado
from application.use_cases.consultar_cliente import ConsultarClienteUseCase
from application.use_cases.consultar_historico_cliente import ConsultarHistoricoClienteUseCase
from application.use_cases.registrar_novo_contato import ContatoRegistrado
from domain.value_objects.tipo_interacao import TipoInteracao

pytestmark = pytest.mark.unit


def as_(hora: int, dia: int = 15) -> datetime:
    return datetime(2026, 9, dia, hora, 0, tzinfo=UTC)


@pytest.fixture
def consultar_cliente(
    clientes: ClienteRepositoryEmMemoria, orcamentos: OrcamentoRepositoryEmMemoria
) -> ConsultarClienteUseCase:
    return ConsultarClienteUseCase(clientes, orcamentos)


@pytest.fixture
def consultar_historico(
    clientes: ClienteRepositoryEmMemoria, orcamentos: OrcamentoRepositoryEmMemoria
) -> ConsultarHistoricoClienteUseCase:
    return ConsultarHistoricoClienteUseCase(clientes, orcamentos)


# --- Cliente com orçamentos (RF08) -------------------------------------------


def test_cliente_vem_com_todos_os_seus_orcamentos(
    consultar_cliente: ConsultarClienteUseCase,
    orcamentos: OrcamentoRepositoryEmMemoria,
    novo_contato: Callable[..., ContatoRegistrado],
) -> None:
    contato = novo_contato()
    novo_contato(nome="Outro", email="outro@x.com")
    segundo = contato.cliente.abrir_orcamento(hoje=date(2026, 10, 1))
    orcamentos.salvar(segundo)

    resultado = consultar_cliente.executar(contato.cliente.id)

    assert resultado.cliente.id == contato.cliente.id
    assert [o.id for o in resultado.orcamentos] == [contato.orcamento.id, segundo.id]


def test_cliente_inexistente(consultar_cliente: ConsultarClienteUseCase) -> None:
    with pytest.raises(ClienteNaoEncontrado):
        consultar_cliente.executar(uuid4())


# --- Linha do tempo (RF07 / RN08) --------------------------------------------


def test_historico_reune_interacoes_de_todos_os_orcamentos_em_ordem_cronologica(
    consultar_historico: ConsultarHistoricoClienteUseCase,
    orcamentos: OrcamentoRepositoryEmMemoria,
    novo_contato: Callable[..., ContatoRegistrado],
) -> None:
    contato = novo_contato()
    primeiro = contato.orcamento
    segundo = contato.cliente.abrir_orcamento(hoje=date(2026, 9, 15))
    primeiro.registrar_interacao(TipoInteracao.MENSAGEM, "primeiro contato", agora=as_(9))
    segundo.registrar_interacao(TipoInteracao.LIGACAO, "novo pedido", agora=as_(11))
    primeiro.registrar_interacao(TipoInteracao.REUNIAO, "visita", agora=as_(10))
    orcamentos.salvar(primeiro)
    orcamentos.salvar(segundo)

    historico = consultar_historico.executar(contato.cliente.id)

    assert [item.interacao.conteudo for item in historico] == [
        "primeiro contato",
        "visita",
        "novo pedido",
    ]
    assert [item.orcamento_id for item in historico] == [primeiro.id, primeiro.id, segundo.id]


def test_historico_nao_mistura_clientes(
    consultar_historico: ConsultarHistoricoClienteUseCase,
    orcamentos: OrcamentoRepositoryEmMemoria,
    novo_contato: Callable[..., ContatoRegistrado],
) -> None:
    maria = novo_contato()
    joao = novo_contato(nome="João", email="joao@x.com")
    joao.orcamento.registrar_interacao(TipoInteracao.MENSAGEM, "do João", agora=as_(9))
    orcamentos.salvar(joao.orcamento)

    assert consultar_historico.executar(maria.cliente.id) == []


def test_historico_de_cliente_inexistente(
    consultar_historico: ConsultarHistoricoClienteUseCase,
) -> None:
    with pytest.raises(ClienteNaoEncontrado):
        consultar_historico.executar(uuid4())
