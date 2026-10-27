"""Apoio aos testes de integração: bancos disponíveis e conjunto de repositórios (RNF08).

- SQLite em memória: roda sempre, sem instalar nada.
- PostgreSQL: roda quando TEST_DATABASE_URL (variável de ambiente ou .env) aponta para
  um banco de teste — o do Supabase ou o do `docker compose up`.
"""

import os
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass

import pytest
from sqlalchemy.orm import Session, sessionmaker

from domain.repositories.cliente_repository import ClienteRepository
from domain.repositories.orcamento_repository import OrcamentoRepository
from domain.repositories.usuario_repository import UsuarioRepository
from infra.config import Configuracao
from infra.db.models import Base
from infra.db.session import criar_engine, criar_fabrica_sessoes

BANCOS_SQL = ["sqlite", "postgres"]


def url_do_banco(nome: str) -> str:
    if nome == "sqlite":
        return "sqlite://"
    configuracao = Configuracao()
    url = os.environ.get("TEST_DATABASE_URL") or configuracao.test_database_url
    if not url:
        pytest.skip("TEST_DATABASE_URL não definida — PostgreSQL de teste indisponível")
    if url == configuracao.database_url:
        pytest.fail(
            "TEST_DATABASE_URL aponta para o banco da aplicação: os testes apagariam os dados."
        )
    return url


@contextmanager
def banco_limpo(nome: str) -> Iterator[sessionmaker[Session]]:
    """Cria as tabelas, entrega a fábrica de sessões e apaga tudo ao final."""
    engine = criar_engine(url_do_banco(nome))
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    try:
        yield criar_fabrica_sessoes(engine)
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()


@dataclass(frozen=True)
class Repositorios:
    clientes: ClienteRepository
    orcamentos: OrcamentoRepository
    usuarios: UsuarioRepository
