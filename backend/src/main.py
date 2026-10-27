"""Composition root: monta a aplicação e escolhe as implementações concretas.

Rodar em desenvolvimento (PowerShell, dentro de backend/):
    .\\.venv\\Scripts\\python.exe -m uvicorn main:app --app-dir src --reload
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, sessionmaker

from adapters.controllers import (
    auth_controller,
    cliente_controller,
    interacao_controller,
    metricas_controller,
    orcamento_controller,
    usuario_controller,
)
from adapters.controllers.dependencias import obter_usuario_logado
from adapters.controllers.erros import registrar_tratadores_de_erro
from application.portas import HashDeSenha
from application.relogio import Relogio
from infra.config import SEGREDO_JWT_PADRAO, Configuracao
from infra.db.session import criar_engine, criar_fabrica_sessoes
from infra.security import EmissorJWT, HashScrypt


def relogio_no_fuso(fuso: str) -> Relogio:
    """Hora atual no fuso do negócio.

    A data de abertura e de fechamento de um orçamento é a data local: às 22h em
    Brasília já é o dia seguinte em UTC. Os horários são gravados em UTC pelo banco.
    """
    zona = ZoneInfo(fuso)

    def agora() -> datetime:
        return datetime.now(zona)

    return agora


def criar_app(
    configuracao: Configuracao | None = None,
    fabrica_sessoes: sessionmaker[Session] | None = None,
    relogio: Relogio | None = None,
    hash_de_senha: HashDeSenha | None = None,
) -> FastAPI:
    """Os testes passam banco, relógio e hash próprios; em produção, tudo vem da configuração."""
    config = configuracao or Configuracao()
    if config.environment == "production" and config.jwt_secret == SEGREDO_JWT_PADRAO:
        raise RuntimeError("Defina JWT_SECRET: o segredo padrão não pode ser usado em produção.")

    @asynccontextmanager
    async def ciclo_de_vida(app: FastAPI) -> AsyncIterator[None]:
        # A conexão com o banco só é criada quando o servidor sobe, não ao importar o módulo.
        engine = None
        if app.state.fabrica_sessoes is None:
            engine = criar_engine(config.database_url)
            app.state.fabrica_sessoes = criar_fabrica_sessoes(engine)
        yield
        if engine is not None:
            engine.dispose()

    app = FastAPI(
        title="CRM de Atendimento e Orçamentos",
        version="0.1.0",
        lifespan=ciclo_de_vida,
    )
    app.state.fabrica_sessoes = fabrica_sessoes
    app.state.relogio = relogio or relogio_no_fuso(config.fuso_horario)
    app.state.hash_de_senha = hash_de_senha or HashScrypt()
    app.state.emissor_token = EmissorJWT(
        config.jwt_secret, config.jwt_algorithm, config.jwt_expiration_minutes, app.state.relogio
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.origens_cors,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    registrar_tratadores_de_erro(app)

    # Login e gestão de usuários tratam a autenticação por conta própria.
    app.include_router(auth_controller.router, prefix=config.api_v1_prefix)
    app.include_router(usuario_controller.router, prefix=config.api_v1_prefix)
    # Todas as rotas do CRM exigem um token válido (RNF07).
    exige_login = [Depends(obter_usuario_logado)]
    for modulo in (
        cliente_controller,
        orcamento_controller,
        interacao_controller,
        metricas_controller,
    ):
        app.include_router(modulo.router, prefix=config.api_v1_prefix, dependencies=exige_login)
    return app


app = criar_app()
