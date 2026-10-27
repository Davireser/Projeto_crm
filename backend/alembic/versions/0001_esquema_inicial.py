"""Esquema inicial: usuario, cliente, orcamento e interacao (05-diagrama-er.md).

Revision ID: 0001
Revises:
Create Date: 2026-10-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

from infra.db.models import DataHoraUTC

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Valores fixos nesta revisão: uma migration é um retrato do esquema naquele
# momento e não deve mudar se os enums do domínio mudarem depois.
PERFIS = "'USUARIO', 'ADMINISTRADOR'"
ESTAGIOS = "'NOVO_CONTATO', 'EM_NEGOCIACAO', 'ORCAMENTO_ENVIADO', 'FECHADO', 'PERDIDO'"
TIPOS = "'MENSAGEM', 'LIGACAO', 'REUNIAO'"


def upgrade() -> None:
    op.create_table(
        "usuario",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("nome", sa.String(120), nullable=False),
        sa.Column("email", sa.String(254), nullable=False, unique=True),
        sa.Column("senha_hash", sa.String(255), nullable=False),
        sa.Column("perfil", sa.String(20), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False),
        sa.CheckConstraint(f"perfil IN ({PERFIS})", name="ck_usuario_perfil"),
    )
    op.create_table(
        "cliente",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("nome", sa.String(120), nullable=False),
        sa.Column("telefone", sa.String(11), nullable=False),
        sa.Column("email", sa.String(254), nullable=False),
        sa.Column("empresa", sa.String(120), nullable=True),
        sa.Column("tipo_embalagem_interesse", sa.String(120), nullable=True),
        sa.Column("criado_em", DataHoraUTC(), nullable=False),
    )
    op.create_table(
        "orcamento",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "cliente_id",
            sa.Uuid(),
            sa.ForeignKey("cliente.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("estagio", sa.String(20), nullable=False),
        # Nullable de propósito: orçamento ainda sem preço é um estado válido (RF03).
        sa.Column("valor", sa.Numeric(12, 2), nullable=True),
        sa.Column("data_abertura", sa.Date(), nullable=False),
        sa.Column("data_fechamento", sa.Date(), nullable=True),
        sa.CheckConstraint(f"estagio IN ({ESTAGIOS})", name="ck_orcamento_estagio"),
    )
    op.create_index("idx_orcamento_estagio", "orcamento", ["estagio"])
    op.create_index("idx_orcamento_cliente_id", "orcamento", ["cliente_id"])
    op.create_table(
        "interacao",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "orcamento_id",
            sa.Uuid(),
            sa.ForeignKey("orcamento.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("tipo", sa.String(10), nullable=False),
        sa.Column("conteudo", sa.Text(), nullable=False),
        sa.Column("data_hora", DataHoraUTC(), nullable=False),
        sa.CheckConstraint(f"tipo IN ({TIPOS})", name="ck_interacao_tipo"),
    )
    op.create_index(
        "idx_interacao_orcamento_data", "interacao", ["orcamento_id", sa.text("data_hora DESC")]
    )


def downgrade() -> None:
    op.drop_index("idx_interacao_orcamento_data", table_name="interacao")
    op.drop_table("interacao")
    op.drop_index("idx_orcamento_cliente_id", table_name="orcamento")
    op.drop_index("idx_orcamento_estagio", table_name="orcamento")
    op.drop_table("orcamento")
    op.drop_table("cliente")
    op.drop_table("usuario")
