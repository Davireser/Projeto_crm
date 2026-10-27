"""Ambiente do Alembic: liga as migrations aos models e à URL do banco."""

from logging.config import fileConfig

from alembic import context

from infra.config import Configuracao
from infra.db.models import Base
from infra.db.session import criar_engine

config = context.config
if config.config_file_name is not None and config.attributes.get("configurar_log", True):
    fileConfig(config.config_file_name, disable_existing_loggers=False)

target_metadata = Base.metadata


def _url() -> str:
    # Uma URL definida explicitamente (ex.: pelos testes) vence a do ambiente.
    return config.get_main_option("sqlalchemy.url") or Configuracao().database_url


def executar_offline() -> None:
    """Gera o SQL sem conectar ao banco: alembic upgrade head --sql."""
    context.configure(url=_url(), target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def executar_online() -> None:
    engine = criar_engine(_url())
    with engine.connect() as conexao:
        context.configure(
            connection=conexao,
            target_metadata=target_metadata,
            render_as_batch=conexao.dialect.name == "sqlite",
        )
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()


if context.is_offline_mode():
    executar_offline()
else:
    executar_online()
