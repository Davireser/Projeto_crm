"""Fixtures dos testes de casos de uso: repositórios em memória e relógio fixo (RNF06)."""

from collections.abc import Callable
from datetime import UTC, datetime

import pytest

from adapters.repositories.em_memoria import (
    ClienteRepositoryEmMemoria,
    OrcamentoRepositoryEmMemoria,
)
from application.relogio import Relogio
from application.use_cases.registrar_novo_contato import (
    ContatoRegistrado,
    DadosNovoContato,
    RegistrarNovoContatoUseCase,
)

AGORA = datetime(2026, 9, 15, 14, 30, tzinfo=UTC)


@pytest.fixture
def agora() -> datetime:
    return AGORA


@pytest.fixture
def relogio() -> Relogio:
    return lambda: AGORA


@pytest.fixture
def clientes() -> ClienteRepositoryEmMemoria:
    return ClienteRepositoryEmMemoria()


@pytest.fixture
def orcamentos() -> OrcamentoRepositoryEmMemoria:
    return OrcamentoRepositoryEmMemoria()


@pytest.fixture
def novo_contato(
    clientes: ClienteRepositoryEmMemoria,
    orcamentos: OrcamentoRepositoryEmMemoria,
    relogio: Relogio,
) -> Callable[..., ContatoRegistrado]:
    """Atalho para registrar um contato válido pelo próprio caso de uso."""
    use_case = RegistrarNovoContatoUseCase(clientes, orcamentos, relogio)

    def registrar(
        nome: str = "Maria Souza", email: str = "maria@embalagensabc.com.br"
    ) -> ContatoRegistrado:
        return use_case.executar(
            DadosNovoContato(nome=nome, telefone="(31) 99876-5432", email=email)
        )

    return registrar
