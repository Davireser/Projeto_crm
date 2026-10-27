"""Fixtures de banco e de API para os testes de integração."""

from collections.abc import Iterator
from datetime import UTC, datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from adapters.repositories.cliente_repository_postgres import ClienteRepositoryPostgres
from adapters.repositories.em_memoria import (
    ClienteRepositoryEmMemoria,
    OrcamentoRepositoryEmMemoria,
    UsuarioRepositoryEmMemoria,
)
from adapters.repositories.orcamento_repository_postgres import OrcamentoRepositoryPostgres
from adapters.repositories.usuario_repository_postgres import UsuarioRepositoryPostgres
from apoio_api import cadastrar, entrar_como, montar_app, novo_usuario
from apoio_banco import BANCOS_SQL, Repositorios, banco_limpo
from domain.entities.usuario import Usuario
from relogio_de_teste import RelogioDeTeste

AGORA = datetime(2026, 9, 15, 14, 30, tzinfo=UTC)


@pytest.fixture(params=BANCOS_SQL)
def fabrica(request: pytest.FixtureRequest) -> Iterator[sessionmaker[Session]]:
    with banco_limpo(request.param) as fabrica_de_sessoes:
        yield fabrica_de_sessoes


@pytest.fixture
def sessao(fabrica: sessionmaker[Session]) -> Iterator[Session]:
    with fabrica() as sessao_aberta:
        yield sessao_aberta
        sessao_aberta.rollback()


@pytest.fixture(params=["memoria", *BANCOS_SQL])
def repos(request: pytest.FixtureRequest) -> Iterator[Repositorios]:
    """O mesmo contrato, exercitado em cada implementação de repositório."""
    if request.param == "memoria":
        yield Repositorios(
            ClienteRepositoryEmMemoria(),
            OrcamentoRepositoryEmMemoria(),
            UsuarioRepositoryEmMemoria(),
        )
        return
    with banco_limpo(request.param) as fabrica_de_sessoes, fabrica_de_sessoes() as sessao_aberta:
        yield Repositorios(
            ClienteRepositoryPostgres(sessao_aberta),
            OrcamentoRepositoryPostgres(sessao_aberta),
            UsuarioRepositoryPostgres(sessao_aberta),
        )
        sessao_aberta.rollback()


@pytest.fixture
def relogio_api() -> RelogioDeTeste:
    return RelogioDeTeste(AGORA)


@pytest.fixture
def app(fabrica: sessionmaker[Session], relogio_api: RelogioDeTeste) -> FastAPI:
    """A aplicação ligada a um banco de teste limpo, com relógio controlado."""
    return montar_app(fabrica, relogio_api)


@pytest.fixture
def admin(fabrica: sessionmaker[Session]) -> Usuario:
    return cadastrar(fabrica, novo_usuario("Admin", "admin@crm.com", administrador=True))


@pytest.fixture
def api_anonima(app: FastAPI) -> Iterator[TestClient]:
    """Cliente HTTP sem login."""
    with TestClient(app) as cliente:
        yield cliente


@pytest.fixture
def api(app: FastAPI, admin: Usuario) -> Iterator[TestClient]:
    """Cliente HTTP já autenticado como administrador."""
    with TestClient(app) as cliente:
        yield entrar_como(cliente, admin)
