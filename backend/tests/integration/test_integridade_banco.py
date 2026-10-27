"""Integridade garantida pelo próprio banco (RNF08, 05-diagrama-er.md).

O banco é a última linha de defesa: mesmo uma escrita direta, sem passar pelo
domínio, não consegue quebrar estas restrições.
"""

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, date, datetime
from uuid import uuid4

import pytest
from sqlalchemy import delete, func, insert, select
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.orm import Session

from adapters.repositories.cliente_repository_postgres import ClienteRepositoryPostgres
from adapters.repositories.orcamento_repository_postgres import OrcamentoRepositoryPostgres
from adapters.repositories.usuario_repository_postgres import UsuarioRepositoryPostgres
from domain.entities.cliente import Cliente
from domain.entities.orcamento import Orcamento
from domain.entities.usuario import Usuario
from domain.value_objects.email import Email
from domain.value_objects.telefone import Telefone
from domain.value_objects.tipo_interacao import TipoInteracao
from infra.db.models import ClienteModel, InteracaoModel, OrcamentoModel

pytestmark = pytest.mark.integration

AGORA = datetime(2026, 9, 15, 14, 30, tzinfo=UTC)


@contextmanager
def recusado_pelo_banco() -> Iterator[None]:
    """Confere que o banco recusou por restrição de integridade (SQLSTATE classe 23).

    O SQLite entrega IntegrityError. O pg8000 só entrega IntegrityError para UNIQUE;
    CHECK e FOREIGN KEY chegam como ProgrammingError — por isso o teste olha o
    código do PostgreSQL, e não o nome da classe.
    """
    with pytest.raises(DBAPIError) as erro:
        yield
    if isinstance(erro.value, IntegrityError):
        return
    argumentos = getattr(erro.value.orig, "args", ())
    detalhes = argumentos[0] if argumentos and isinstance(argumentos[0], dict) else {}
    assert str(detalhes.get("C", "")).startswith("23"), f"não é violação de integridade: {erro}"


def orcamento_com_interacao(sessao: Session) -> tuple[Cliente, Orcamento]:
    cliente = Cliente.cadastrar(
        nome="Maria", telefone=Telefone("31998765432"), email=Email("m@x.com"), agora=AGORA
    )
    ClienteRepositoryPostgres(sessao).salvar(cliente)
    orcamento = cliente.abrir_orcamento(hoje=AGORA.date())
    orcamento.registrar_interacao(TipoInteracao.MENSAGEM, "Oi", agora=AGORA)
    OrcamentoRepositoryPostgres(sessao).salvar(orcamento)
    return cliente, orcamento


def test_cliente_com_historico_nao_pode_ser_apagado(sessao: Session) -> None:
    cliente, _ = orcamento_com_interacao(sessao)

    with recusado_pelo_banco():
        sessao.execute(delete(ClienteModel).where(ClienteModel.id == cliente.id))


def test_apagar_orcamento_apaga_suas_interacoes(sessao: Session) -> None:
    _, orcamento = orcamento_com_interacao(sessao)
    sessao.expunge_all()

    sessao.execute(delete(OrcamentoModel).where(OrcamentoModel.id == orcamento.id))

    restantes = sessao.scalar(
        select(func.count())
        .select_from(InteracaoModel)
        .where(InteracaoModel.orcamento_id == orcamento.id)
    )
    assert restantes == 0


def test_banco_recusa_estagio_fora_do_funil(sessao: Session) -> None:
    cliente, _ = orcamento_com_interacao(sessao)

    with recusado_pelo_banco():
        sessao.execute(
            insert(OrcamentoModel).values(
                id=uuid4(), cliente_id=cliente.id, estagio="QUALQUER", data_abertura=date.today()
            )
        )


def test_banco_recusa_tipo_de_interacao_desconhecido(sessao: Session) -> None:
    _, orcamento = orcamento_com_interacao(sessao)

    with recusado_pelo_banco():
        sessao.execute(
            insert(InteracaoModel).values(
                id=uuid4(), orcamento_id=orcamento.id, tipo="EMAIL", conteudo="x", data_hora=AGORA
            )
        )


def test_email_de_usuario_e_unico(sessao: Session) -> None:
    repositorio = UsuarioRepositoryPostgres(sessao)
    repositorio.salvar(Usuario(id=uuid4(), nome="Ana", email=Email("a@crm.com"), senha_hash="h"))

    with recusado_pelo_banco():
        repositorio.salvar(
            Usuario(id=uuid4(), nome="Outra Ana", email=Email("a@crm.com"), senha_hash="h")
        )
