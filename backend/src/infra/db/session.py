"""Engine, fábrica de sessões e transação por requisição."""

import ssl
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from sqlalchemy import URL, Engine, create_engine, event, make_url
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# O pg8000 é um driver de PostgreSQL em Python puro: não depende de DLL compilada,
# que o Smart App Control do Windows pode bloquear; o psycopg nem tem versão 32 bits.
_DRIVER_PADRAO = "postgresql+pg8000"
_SSLMODES = {"disable", "allow", "prefer", "require", "verify-ca", "verify-full"}


def criar_engine(url: str) -> Engine:
    if not url.startswith("sqlite"):
        url_final, argumentos = preparar_conexao(url)
        return create_engine(url_final, pool_pre_ping=True, connect_args=argumentos)

    opcoes: dict[str, Any] = {"connect_args": {"check_same_thread": False}}
    if url in ("sqlite://", "sqlite:///:memory:"):
        # Banco em memória: todas as sessões precisam enxergar a mesma conexão.
        opcoes["poolclass"] = StaticPool
    engine = create_engine(url, **opcoes)
    event.listen(engine, "connect", _ligar_chaves_estrangeiras_no_sqlite)
    return engine


def preparar_conexao(url: str) -> tuple[URL, dict[str, Any]]:
    """Aceita a URL como o Supabase/PostgreSQL mostra (postgresql://...?sslmode=require).

    Troca o driver para o pg8000 e traduz o `sslmode` do libpq — que o pg8000 não
    entende — em um contexto SSL. URLs de outros drivers passam sem mudança.
    """
    final = make_url(url)
    if final.drivername in ("postgres", "postgresql"):
        final = final.set(drivername=_DRIVER_PADRAO)
    if final.drivername != _DRIVER_PADRAO:
        return final, {}

    parametros = dict(final.query)
    modo = parametros.pop("sslmode", None)
    certificado_raiz = parametros.pop("sslrootcert", None)
    final = final.set(query=parametros)
    contexto = _contexto_ssl(
        modo if isinstance(modo, str) else None,
        certificado_raiz if isinstance(certificado_raiz, str) else None,
    )
    return final, ({"ssl_context": contexto} if contexto else {})


def _contexto_ssl(modo: str | None, certificado_raiz: str | None) -> ssl.SSLContext | None:
    """Mesmo significado do libpq: `require` criptografa; `verify-*` confere o certificado."""
    if modo is not None and modo not in _SSLMODES:
        raise ValueError(f"sslmode desconhecido: {modo!r}")
    if modo in (None, "disable", "allow", "prefer"):
        return None
    contexto = ssl.create_default_context(cafile=certificado_raiz)
    if modo == "require" and certificado_raiz is None:
        contexto.check_hostname = False
        contexto.verify_mode = ssl.CERT_NONE
    else:
        contexto.check_hostname = modo == "verify-full"
    return contexto


def _ligar_chaves_estrangeiras_no_sqlite(conexao: Any, _registro: Any) -> None:
    # O SQLite só aplica FOREIGN KEY (RESTRICT/CASCADE) com esta opção ligada.
    cursor = conexao.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def criar_fabrica_sessoes(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False)


@contextmanager
def sessao_transacional(fabrica: sessionmaker[Session]) -> Iterator[Session]:
    """Uma transação por requisição: confirma tudo no fim ou desfaz tudo se algo falhar."""
    sessao = fabrica()
    try:
        yield sessao
        sessao.commit()
    except BaseException:
        sessao.rollback()
        raise
    finally:
        sessao.close()
