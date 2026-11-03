"""Redefine a senha de um usuário pelo e-mail (para quem esqueceu, inclusive o administrador).

Uso no Docker (PowerShell, na raiz do projeto):
    docker compose exec api python src/redefinir_senha.py --email voce@email.com
Uso local (PowerShell, dentro de backend/):
    .\\.venv\\Scripts\\python.exe src\\redefinir_senha.py --email voce@email.com
A nova senha é pedida no terminal, sem aparecer na tela.
"""

import argparse
import getpass
import sys

from sqlalchemy.orm import Session, sessionmaker

from adapters.repositories.usuario_repository_postgres import UsuarioRepositoryPostgres
from application.exceptions import EmailNaoCadastrado
from application.portas import HashDeSenha
from application.use_cases.gerenciar_usuarios import GerenciarUsuariosUseCase
from domain.entities.usuario import Usuario
from domain.exceptions import ErroDominio
from infra.config import Configuracao
from infra.db.session import criar_engine, criar_fabrica_sessoes, sessao_transacional
from infra.security import HashScrypt


def redefinir_senha(
    fabrica: sessionmaker[Session], hash_de_senha: HashDeSenha, email: str, nova_senha: str
) -> Usuario:
    with sessao_transacional(fabrica) as sessao:
        use_case = GerenciarUsuariosUseCase(UsuarioRepositoryPostgres(sessao), hash_de_senha)
        return use_case.redefinir_senha(email, nova_senha)


def main(argumentos: list[str] | None = None) -> int:
    leitor = argparse.ArgumentParser(description="Redefine a senha de um usuário do CRM.")
    leitor.add_argument("--email", required=True)
    opcoes = leitor.parse_args(argumentos)

    senha = getpass.getpass("Nova senha (mínimo 8 caracteres): ")
    if senha != getpass.getpass("Repita a nova senha: "):
        print("As senhas não conferem.", file=sys.stderr)
        return 1

    engine = criar_engine(Configuracao().database_url)
    try:
        usuario = redefinir_senha(criar_fabrica_sessoes(engine), HashScrypt(), opcoes.email, senha)
    except (ErroDominio, EmailNaoCadastrado) as erro:
        print(f"Não foi possível redefinir: {erro.mensagem}", file=sys.stderr)
        return 1
    finally:
        engine.dispose()

    print(f"Senha redefinida: {usuario.nome} <{usuario.email.endereco}>")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
