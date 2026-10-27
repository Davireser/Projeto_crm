"""Models ORM — o formato das tabelas (05-diagrama-er.md).

Estes models NÃO são as entidades do domínio. A tradução model ↔ entidade
acontece nos repositórios em adapters/repositories/.
"""

from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Dialect,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    TypeDecorator,
    Uuid,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from domain.entities.usuario import Perfil
from domain.value_objects.estagio_atendimento import EstagioAtendimento
from domain.value_objects.tipo_interacao import TipoInteracao


def _valores_permitidos(coluna: str, valores: list[str]) -> str:
    lista = ", ".join(f"'{valor}'" for valor in valores)
    return f"{coluna} IN ({lista})"


class DataHoraUTC(TypeDecorator[datetime]):
    """Grava sempre em UTC e devolve sempre com fuso horário.

    O PostgreSQL guarda o fuso (timestamptz); o SQLite não — sem isto, o
    SQLite devolveria datas "ingênuas" e a comparação com o domínio falharia.
    """

    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect: Dialect) -> datetime | None:
        return value.astimezone(UTC) if value is not None else None

    def process_result_value(self, value: datetime | None, dialect: Dialect) -> datetime | None:
        if value is None:
            return None
        return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


class Base(DeclarativeBase):
    pass


class UsuarioModel(Base):
    __tablename__ = "usuario"
    __table_args__ = (
        CheckConstraint(
            _valores_permitidos("perfil", [p.value for p in Perfil]), "ck_usuario_perfil"
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(254), unique=True)
    senha_hash: Mapped[str] = mapped_column(String(255))
    perfil: Mapped[str] = mapped_column(String(20))
    ativo: Mapped[bool]


class ClienteModel(Base):
    __tablename__ = "cliente"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    telefone: Mapped[str] = mapped_column(String(11))
    email: Mapped[str] = mapped_column(String(254))
    empresa: Mapped[str | None] = mapped_column(String(120))
    tipo_embalagem_interesse: Mapped[str | None] = mapped_column(String(120))
    criado_em: Mapped[datetime] = mapped_column(DataHoraUTC)


class OrcamentoModel(Base):
    __tablename__ = "orcamento"
    __table_args__ = (
        CheckConstraint(
            _valores_permitidos("estagio", [e.value for e in EstagioAtendimento]),
            "ck_orcamento_estagio",
        ),
        Index("idx_orcamento_estagio", "estagio"),
        Index("idx_orcamento_cliente_id", "cliente_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    cliente_id: Mapped[UUID] = mapped_column(ForeignKey("cliente.id", ondelete="RESTRICT"))
    estagio: Mapped[str] = mapped_column(String(20))
    valor: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    data_abertura: Mapped[date] = mapped_column(Date)
    data_fechamento: Mapped[date | None] = mapped_column(Date)

    interacoes: Mapped[list["InteracaoModel"]] = relationship(
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="InteracaoModel.data_hora",
        lazy="selectin",
    )


class InteracaoModel(Base):
    __tablename__ = "interacao"
    __table_args__ = (
        CheckConstraint(
            _valores_permitidos("tipo", [t.value for t in TipoInteracao]), "ck_interacao_tipo"
        ),
        Index("idx_interacao_orcamento_data", "orcamento_id", text("data_hora DESC")),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    orcamento_id: Mapped[UUID] = mapped_column(ForeignKey("orcamento.id", ondelete="CASCADE"))
    tipo: Mapped[str] = mapped_column(String(10))
    conteudo: Mapped[str] = mapped_column(Text)
    data_hora: Mapped[datetime] = mapped_column(DataHoraUTC)
