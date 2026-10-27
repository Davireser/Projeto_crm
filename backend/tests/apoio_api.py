"""Apoio aos testes da API: monta a aplicação, cadastra usuários e entra com eles."""

from typing import Any
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from adapters.repositories.usuario_repository_postgres import UsuarioRepositoryPostgres
from domain.entities.usuario import Administrador, Usuario
from domain.value_objects.email import Email
from infra.config import Configuracao
from infra.db.session import sessao_transacional
from infra.security import HashScrypt
from main import criar_app
from relogio_de_teste import RelogioDeTeste

SENHA = "senha-de-teste"
# Custo baixo só para os testes ficarem rápidos; a aplicação usa o padrão.
HASH_RAPIDO = HashScrypt(n=2**10)


def montar_app(
    fabrica: sessionmaker[Session], relogio: RelogioDeTeste, **configuracao: Any
) -> FastAPI:
    return criar_app(
        configuracao=Configuracao(_env_file=None, **configuracao),
        fabrica_sessoes=fabrica,
        relogio=relogio,
        hash_de_senha=HASH_RAPIDO,
    )


def novo_usuario(nome: str, email: str, *, administrador: bool = False) -> Usuario:
    classe = Administrador if administrador else Usuario
    return classe(id=uuid4(), nome=nome, email=Email(email), senha_hash=HASH_RAPIDO.gerar(SENHA))


def cadastrar(fabrica: sessionmaker[Session], usuario: Usuario) -> Usuario:
    with sessao_transacional(fabrica) as sessao:
        UsuarioRepositoryPostgres(sessao).salvar(usuario)
    return usuario


def entrar_como(cliente: TestClient, usuario: Usuario) -> TestClient:
    """Coloca no cliente HTTP o token do usuário, como o frontend faria após o login."""
    app = cliente.app
    assert isinstance(app, FastAPI)
    token = app.state.emissor_token.emitir(usuario).valor
    cliente.headers["Authorization"] = f"Bearer {token}"
    return cliente
