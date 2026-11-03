"""Comando de redefinir senha: recupera o acesso de quem esqueceu a senha (até do admin)."""

import getpass
from collections.abc import Iterator
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session, sessionmaker

from adapters.repositories.usuario_repository_postgres import UsuarioRepositoryPostgres
from apoio_api import HASH_RAPIDO
from domain.entities.usuario import Administrador
from domain.value_objects.email import Email
from infra.db.models import Base
from infra.db.session import criar_engine, criar_fabrica_sessoes, sessao_transacional
from infra.security import HashScrypt
from redefinir_senha import main, redefinir_senha

pytestmark = pytest.mark.integration


def salvar_admin(fabrica: sessionmaker[Session]) -> None:
    with sessao_transacional(fabrica) as sessao:
        UsuarioRepositoryPostgres(sessao).salvar(
            Administrador(
                id=uuid4(),
                nome="Dona Maria",
                email=Email("maria@embalagens.com"),
                senha_hash=HASH_RAPIDO.gerar("esqueci-esta"),
            )
        )


def test_redefine_a_senha(fabrica: sessionmaker[Session]) -> None:
    salvar_admin(fabrica)

    redefinir_senha(fabrica, HASH_RAPIDO, "maria@embalagens.com", "senha-nova-1")

    with fabrica() as sessao:
        salvo = UsuarioRepositoryPostgres(sessao).buscar_por_email(Email("maria@embalagens.com"))
    assert isinstance(salvo, Administrador)
    assert HASH_RAPIDO.confere("senha-nova-1", salvo.senha_hash)
    assert not HASH_RAPIDO.confere("esqueci-esta", salvo.senha_hash)


@pytest.fixture
def banco_em_arquivo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[str]:
    """O comando lê DATABASE_URL da configuração; aqui ela aponta para um SQLite descartável."""
    url = f"sqlite:///{tmp_path / 'crm.db'}"
    engine = criar_engine(url)
    Base.metadata.create_all(engine)
    salvar_admin(criar_fabrica_sessoes(engine))
    engine.dispose()
    monkeypatch.setenv("DATABASE_URL", url)
    yield url


def digitar_senhas(monkeypatch: pytest.MonkeyPatch, *senhas: str) -> None:
    respostas = iter(senhas)
    monkeypatch.setattr(getpass, "getpass", lambda _pergunta: next(respostas))


def test_comando_redefine_e_a_nova_senha_funciona(
    banco_em_arquivo: str, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    digitar_senhas(monkeypatch, "senha-nova-1", "senha-nova-1")

    codigo = main(["--email", "maria@embalagens.com"])

    assert codigo == 0
    assert "Senha redefinida: Dona Maria <maria@embalagens.com>" in capsys.readouterr().out
    engine = criar_engine(banco_em_arquivo)
    with criar_fabrica_sessoes(engine)() as sessao:
        salvo = UsuarioRepositoryPostgres(sessao).buscar_por_email(Email("maria@embalagens.com"))
    engine.dispose()
    assert salvo is not None
    assert HashScrypt().confere("senha-nova-1", salvo.senha_hash)


def test_comando_recusa_senhas_diferentes(
    banco_em_arquivo: str, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    digitar_senhas(monkeypatch, "senha-nova-1", "senha-nova-2")

    assert main(["--email", "maria@embalagens.com"]) == 1
    assert "não conferem" in capsys.readouterr().err


@pytest.mark.parametrize(
    ("email", "senha", "mensagem"),
    [
        ("maria@embalagens.com", "curta", "pelo menos 8 caracteres"),
        ("ninguem@x.com", "senha-nova-1", "Nenhum usuário com o e-mail ninguem@x.com"),
    ],
)
def test_comando_mostra_o_motivo_da_recusa(
    banco_em_arquivo: str,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    email: str,
    senha: str,
    mensagem: str,
) -> None:
    digitar_senhas(monkeypatch, senha, senha)

    assert main(["--email", email]) == 1
    assert mensagem in capsys.readouterr().err
