"""Migration Alembic (backlog 1.8): cria exatamente o esquema dos models ORM."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from sqlalchemy import Engine, inspect, text
from sqlalchemy.schema import SchemaItem

from apoio_banco import url_do_banco
from infra.db.models import Base
from infra.db.session import criar_engine

pytestmark = pytest.mark.integration

BACKEND = Path(__file__).resolve().parents[2]
TABELAS = {"usuario", "cliente", "orcamento", "interacao"}
INDICE_COM_EXPRESSAO = "idx_interacao_orcamento_data"


def configuracao(url: str) -> Config:
    config = Config(str(BACKEND / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND / "alembic"))
    config.set_main_option("sqlalchemy.url", url)
    return config


@pytest.fixture(params=["sqlite", "postgres"])
def banco(request: pytest.FixtureRequest, tmp_path: Path) -> Iterator[tuple[Config, Engine]]:
    url = f"sqlite:///{tmp_path / 'crm.db'}" if request.param == "sqlite" else None
    url = url or url_do_banco(request.param)
    engine = criar_engine(url)
    Base.metadata.drop_all(engine)
    with engine.begin() as conexao:
        conexao.exec_driver_sql("DROP TABLE IF EXISTS alembic_version")
    # Descarta as conexões usadas no preparo: elas guardam em cache o esquema
    # de antes da migration e esconderiam os índices recém-criados.
    engine.dispose()
    config = configuracao(url)
    yield config, engine
    command.downgrade(config, "base")
    engine.dispose()


def test_upgrade_cria_as_quatro_tabelas(banco: tuple[Config, Engine]) -> None:
    config, engine = banco

    command.upgrade(config, "head")

    assert set(inspect(engine).get_table_names()) >= TABELAS


def ignorar_indice_com_expressao(
    objeto: SchemaItem, nome: str | None, tipo: str, refletido: bool, comparado: SchemaItem | None
) -> bool:
    # Índice com "data_hora DESC" não é refletido com fidelidade pelos bancos;
    # a existência dele é verificada à parte, pelo nome.
    return not (tipo == "index" and nome == INDICE_COM_EXPRESSAO)


def test_migration_e_models_estao_sincronizados(banco: tuple[Config, Engine]) -> None:
    config, engine = banco
    command.upgrade(config, "head")

    with engine.connect() as conexao:
        contexto = MigrationContext.configure(
            conexao, opts={"include_object": ignorar_indice_com_expressao}
        )
        diferencas = compare_metadata(contexto, Base.metadata)

    assert diferencas == []


def test_indices_do_er_existem(banco: tuple[Config, Engine]) -> None:
    config, engine = banco
    command.upgrade(config, "head")

    inspetor = inspect(engine)
    indices = {
        indice["name"]
        for tabela in ("orcamento", "interacao")
        for indice in inspetor.get_indexes(tabela)
    }

    assert {"idx_orcamento_estagio", "idx_orcamento_cliente_id", INDICE_COM_EXPRESSAO} <= indices


def test_downgrade_remove_tudo(banco: tuple[Config, Engine]) -> None:
    config, engine = banco
    command.upgrade(config, "head")

    command.downgrade(config, "base")

    assert not TABELAS & set(inspect(engine).get_table_names())


TABELAS_SEM_RLS = """
    select c.relname from pg_class c join pg_namespace n on n.oid = c.relnamespace
    where n.nspname = 'public' and c.relkind = 'r' and not c.relrowsecurity
"""
PAPEIS_DA_API = "select count(*) from pg_roles where rolname in ('anon', 'authenticated')"
PERMISSOES_DA_API = """
    select grantee || ' em ' || table_name from information_schema.role_table_grants
    where table_schema = 'public' and grantee in ('anon', 'authenticated')
"""


def test_tabelas_fechadas_para_a_api_automatica_do_supabase(banco: tuple[Config, Engine]) -> None:
    """Os papéis anon/authenticated (Data API do Supabase) não acessam as tabelas.

    A chave `anon` do Supabase é pública por natureza; sem esta proteção, ela daria
    leitura e escrita em `usuario` (com os hashes de senha) sem passar pelo backend.
    """
    config, engine = banco
    if engine.dialect.name != "postgresql":
        pytest.skip("RLS e papéis da API só existem no PostgreSQL")
    command.upgrade(config, "head")

    with engine.connect() as conexao:
        sem_rls = conexao.execute(text(TABELAS_SEM_RLS)).scalars().all()
        papeis_da_api = conexao.execute(text(PAPEIS_DA_API)).scalar()
        permissoes = conexao.execute(text(PERMISSOES_DA_API)).scalars().all()

    assert sem_rls == []
    if papeis_da_api:
        assert permissoes == []
