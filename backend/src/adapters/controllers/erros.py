"""Converte exceções em respostas no formato único da API (especificações §4):

{"erro": "TransicaoInvalida", "mensagem": "...", "campo": "estagio"}
"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from application.exceptions import (
    AcessoNegado,
    CredenciaisInvalidas,
    EmailJaCadastrado,
    ErroDeAcesso,
    NaoAutenticado,
    RecursoNaoEncontrado,
)
from domain.exceptions import ErroDominio

_STATUS_DE_ACESSO: dict[type[ErroDeAcesso], int] = {
    CredenciaisInvalidas: 401,
    NaoAutenticado: 401,
    AcessoNegado: 403,
    EmailJaCadastrado: 409,
}


def _resposta(
    status: int,
    erro: str,
    mensagem: str,
    campo: str | None,
    cabecalhos: dict[str, str] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={"erro": erro, "mensagem": mensagem, "campo": campo},
        headers=cabecalhos,
    )


def tratar_erro_de_dominio(_request: Request, exc: Exception) -> JSONResponse:
    """Regra de negócio violada → 422 (TransicaoInvalida, FormatoInvalido, ValorInvalido...)."""
    assert isinstance(exc, ErroDominio)
    return _resposta(422, type(exc).__name__, exc.mensagem, exc.campo)


def tratar_nao_encontrado(_request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, RecursoNaoEncontrado)
    return _resposta(404, type(exc).__name__, exc.mensagem, None)


def tratar_erro_de_acesso(_request: Request, exc: Exception) -> JSONResponse:
    """401 sem login ou login recusado; 403 sem perfil; 409 e-mail já cadastrado (RNF07)."""
    assert isinstance(exc, ErroDeAcesso)
    status = _STATUS_DE_ACESSO.get(type(exc), 400)
    # 401 avisa ao cliente HTTP qual esquema de autenticação usar.
    cabecalhos = {"WWW-Authenticate": "Bearer"} if status == 401 else None
    return _resposta(status, type(exc).__name__, exc.mensagem, exc.campo, cabecalhos)


def tratar_dados_invalidos(_request: Request, exc: Exception) -> JSONResponse:
    """JSON fora do contrato (campo ausente, tipo errado, enum desconhecido) → 422."""
    assert isinstance(exc, RequestValidationError)
    primeiro = exc.errors()[0]
    local = primeiro.get("loc", ())
    campo = str(local[-1]) if local else None
    return _resposta(422, "DadosInvalidos", f"{campo}: {primeiro.get('msg', '')}", campo)


def registrar_tratadores_de_erro(app: FastAPI) -> None:
    app.add_exception_handler(ErroDominio, tratar_erro_de_dominio)
    app.add_exception_handler(RecursoNaoEncontrado, tratar_nao_encontrado)
    app.add_exception_handler(ErroDeAcesso, tratar_erro_de_acesso)
    app.add_exception_handler(RequestValidationError, tratar_dados_invalidos)
