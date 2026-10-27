"""Script do primeiro administrador: sem ele, ninguém conseguiria entrar no sistema."""

import getpass
from collections.abc import Iterator
from pathlib import Path

import pytest
from sqlalchemy.orm import Session, sessionmaker

from adapters.repositories.usuario_repository_postgres import UsuarioRepositoryPostgres
from apoio_api import HASH_RAPIDO
from criar_administrador import criar_administrador, main
from domain.entities.usuario import Administrador
from domain.exceptions import OperacaoNaoPermitida
from domain.value_objects.email import Email
from infra.db.models import Base
from infra.db.session import criar_engine

pytestmark = pytest.mark.integration


def test_cria_o_primeiro_administrador(fabrica: sessionmaker[Session]) -> None:
    criar_administrador(fabrica, HASH_RAPIDO, "Dona Maria", "maria@embalagens.com", "senha-forte")

    with fabrica() as sessao:
        salvo = UsuarioRepositoryPostgres(sessao).buscar_por_email(Email("maria@embalagens.com"))
    assert isinstance(salvo, Administrador)
    assert HASH_RAPIDO.confere("senha-forte", salvo.senha_hash)


def test_nao_cria_um_segundo_pelo_script(fabrica: sessionmaker[Session]) -> None:
    criar_administrador(fabrica, HASH_RAPIDO, "Dona Maria", "maria@embalagens.com", "senha-forte")

    with pytest.raises(OperacaoNaoPermitida):
        criar_administrador(fabrica, HASH_RAPIDO, "Intruso", "intruso@x.com", "senha-forte")


@pytest.fixture
def banco_em_arquivo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[str]:
    """O comando lê DATABASE_URL da configuração; aqui ela aponta para um SQLite descartável."""
    url = f"sqlite:///{tmp_path / 'crm.db'}"
    engine = criar_engine(url)
    Base.metadata.create_all(engine)
    engine.dispose()
    monkeypatch.setenv("DATABASE_URL", url)
    yield url


def digitar_senhas(monkeypatch: pytest.MonkeyPatch, *senhas: str) -> None:
    respostas = iter(senhas)
    monkeypatch.setattr(getpass, "getpass", lambda _pergunta: next(respostas))


def test_comando_cria_o_administrador(
    banco_em_arquivo: str, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    digitar_senhas(monkeypatch, "senha-forte", "senha-forte")

    codigo = main(["--nome", "Dona Maria", "--email", "maria@embalagens.com"])

    assert codigo == 0
    assert "Administrador criado: Dona Maria <maria@embalagens.com>" in capsys.readouterr().out


def test_comando_recusa_senhas_diferentes(
    banco_em_arquivo: str, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    digitar_senhas(monkeypatch, "senha-forte", "senha-fraca")

    assert main(["--nome", "Dona Maria", "--email", "maria@embalagens.com"]) == 1
    assert "não conferem" in capsys.readouterr().err


def test_comando_mostra_o_erro_de_dominio(
    banco_em_arquivo: str, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    digitar_senhas(monkeypatch, "curta", "curta")

    assert main(["--nome", "Dona Maria", "--email", "maria@embalagens.com"]) == 1
    assert "Não foi possível criar" in capsys.readouterr().err
