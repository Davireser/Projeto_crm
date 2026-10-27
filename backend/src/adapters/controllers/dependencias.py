"""Injeção de dependências das rotas: sessão por requisição, repositórios, relógio e login.

Os repositórios de uma mesma requisição compartilham a mesma sessão (o FastAPI
guarda o resultado de cada dependência durante a requisição), então tudo o que
um caso de uso grava é confirmado ou desfeito junto.
"""

from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from adapters.repositories.cliente_repository_postgres import ClienteRepositoryPostgres
from adapters.repositories.orcamento_repository_postgres import OrcamentoRepositoryPostgres
from adapters.repositories.usuario_repository_postgres import UsuarioRepositoryPostgres
from application.exceptions import NaoAutenticado
from application.portas import HashDeSenha
from application.relogio import Relogio
from domain.entities.usuario import Usuario
from domain.repositories.cliente_repository import ClienteRepository
from domain.repositories.orcamento_repository import OrcamentoRepository
from domain.repositories.usuario_repository import UsuarioRepository
from infra.db.session import sessao_transacional
from infra.security import EmissorJWT, TokenInvalido

# auto_error=False: a ausência do token vira o nosso erro 401 padronizado.
_bearer = HTTPBearer(auto_error=False)


def obter_sessao(request: Request) -> Iterator[Session]:
    with sessao_transacional(request.app.state.fabrica_sessoes) as sessao:
        yield sessao


def obter_relogio(request: Request) -> Relogio:
    relogio: Relogio = request.app.state.relogio
    return relogio


def obter_hash_de_senha(request: Request) -> HashDeSenha:
    hash_de_senha: HashDeSenha = request.app.state.hash_de_senha
    return hash_de_senha


def obter_emissor_token(request: Request) -> EmissorJWT:
    emissor: EmissorJWT = request.app.state.emissor_token
    return emissor


def obter_clientes(sessao: Annotated[Session, Depends(obter_sessao)]) -> ClienteRepository:
    return ClienteRepositoryPostgres(sessao)


def obter_orcamentos(sessao: Annotated[Session, Depends(obter_sessao)]) -> OrcamentoRepository:
    return OrcamentoRepositoryPostgres(sessao)


def obter_usuarios(sessao: Annotated[Session, Depends(obter_sessao)]) -> UsuarioRepository:
    return UsuarioRepositoryPostgres(sessao)


Clientes = Annotated[ClienteRepository, Depends(obter_clientes)]
Orcamentos = Annotated[OrcamentoRepository, Depends(obter_orcamentos)]
Usuarios = Annotated[UsuarioRepository, Depends(obter_usuarios)]
RelogioDaApp = Annotated[Relogio, Depends(obter_relogio)]
HashDaApp = Annotated[HashDeSenha, Depends(obter_hash_de_senha)]
EmissorDaApp = Annotated[EmissorJWT, Depends(obter_emissor_token)]


def obter_usuario_logado(
    credenciais: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    emissor: EmissorDaApp,
    usuarios: Usuarios,
) -> Usuario:
    """Identifica quem faz a requisição pelo token `Authorization: Bearer ...` (RNF07).

    O usuário é recarregado do banco a cada requisição: quem foi desativado
    perde o acesso na hora, mesmo com um token ainda dentro da validade.
    """
    if credenciais is None:
        raise NaoAutenticado()
    try:
        usuario_id = emissor.ler(credenciais.credentials)
    except TokenInvalido as erro:
        raise NaoAutenticado() from erro
    usuario = usuarios.buscar_por_id(usuario_id)
    if usuario is None or not usuario.ativo:
        raise NaoAutenticado()
    return usuario


UsuarioLogado = Annotated[Usuario, Depends(obter_usuario_logado)]
