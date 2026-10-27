"""Fecha as tabelas para a API automática do Supabase (Data API / PostgREST).

O Supabase dá aos papéis `anon` e `authenticated` acesso a toda tabela criada no
schema public. A chave `anon` é pública por natureza, então, sem esta migration,
qualquer pessoa com ela leria e alteraria os dados — inclusive os hashes de senha
— sem passar pelo backend.

- RLS ligado sem nenhuma política: os papéis da API não enxergam nenhuma linha.
  O backend conecta como dono das tabelas, que não é afetado pelo RLS.
- Permissões de anon/authenticated revogadas, também para tabelas futuras.

Fora do Supabase (PostgreSQL local, Docker) os papéis não existem e só o RLS é
ligado, sem efeito para o backend. No SQLite, nada é feito.

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-12
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TABELAS = ("usuario", "cliente", "orcamento", "interacao", "alembic_version")

REVOGAR_PAPEIS_DA_API = """
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon')
       AND EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
        REVOKE ALL ON ALL TABLES IN SCHEMA public FROM anon, authenticated;
        ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON TABLES FROM anon, authenticated;
    END IF;
END
$$;
"""


def _e_postgresql() -> bool:
    return op.get_context().dialect.name == "postgresql"


def upgrade() -> None:
    if not _e_postgresql():
        return
    for tabela in TABELAS:
        op.execute(f"ALTER TABLE {tabela} ENABLE ROW LEVEL SECURITY")
    op.execute(REVOGAR_PAPEIS_DA_API)


def downgrade() -> None:
    # As permissões dos papéis da API não são devolvidas: reabrir as tabelas para
    # a chave pública do Supabase nunca deve ser um efeito colateral de downgrade.
    if not _e_postgresql():
        return
    for tabela in TABELAS:
        op.execute(f"ALTER TABLE {tabela} DISABLE ROW LEVEL SECURITY")
