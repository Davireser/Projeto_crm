"""URL de conexão: aceita a URL como o Supabase/PostgreSQL mostra e adapta ao pg8000."""

import ssl

import pytest

from infra.db.session import preparar_conexao

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "url",
    [
        "postgresql://usuario:senha@db.exemplo.com:5432/postgres",
        "postgres://usuario:senha@db.exemplo.com:5432/postgres",
        "postgresql+pg8000://usuario:senha@db.exemplo.com:5432/postgres",
    ],
)
def test_url_postgres_usa_o_driver_pg8000(url: str) -> None:
    final, argumentos = preparar_conexao(url)

    assert final.drivername == "postgresql+pg8000"
    assert final.host == "db.exemplo.com"
    assert final.password == "senha"
    assert argumentos == {}


def test_sslmode_require_criptografa_sem_verificar_certificado() -> None:
    final, argumentos = preparar_conexao("postgresql://u:s@h:5432/postgres?sslmode=require")

    contexto = argumentos["ssl_context"]
    assert isinstance(contexto, ssl.SSLContext)
    assert contexto.verify_mode is ssl.CERT_NONE
    assert "sslmode" not in final.query  # o pg8000 não entende o parâmetro do libpq


def test_sslmode_verify_full_confere_certificado_e_nome() -> None:
    _, argumentos = preparar_conexao("postgresql://u:s@h/postgres?sslmode=verify-full")

    contexto = argumentos["ssl_context"]
    assert contexto.verify_mode is ssl.CERT_REQUIRED
    assert contexto.check_hostname


@pytest.mark.parametrize("modo", ["disable", "prefer"])
def test_sslmode_sem_exigencia_nao_liga_ssl(modo: str) -> None:
    final, argumentos = preparar_conexao(f"postgresql://u:s@h/postgres?sslmode={modo}")

    assert argumentos == {}
    assert "sslmode" not in final.query


def test_sslmode_desconhecido_e_rejeitado() -> None:
    with pytest.raises(ValueError, match="sslmode"):
        preparar_conexao("postgresql://u:s@h/postgres?sslmode=talvez")


def test_outros_drivers_ficam_como_estao() -> None:
    final, argumentos = preparar_conexao("postgresql+psycopg://u:s@h/postgres?sslmode=require")

    assert final.drivername == "postgresql+psycopg"
    assert final.query["sslmode"] == "require"
    assert argumentos == {}
