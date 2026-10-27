"""Cria o primeiro administrador do sistema (só funciona com o cadastro de usuários vazio).

Uso (PowerShell, dentro de backend/):
    .\\.venv\\Scripts\\python.exe src\\criar_administrador.py --nome "Maria" --email maria@x.com
A senha é pedida no terminal, sem aparecer na tela.
"""

import argparse
import getpass
import sys

from sqlalchemy.orm import Session, sessionmaker

from adapters.repositories.usuario_repository_postgres import UsuarioRepositoryPostgres
from application.portas import HashDeSenha
from application.use_cases.gerenciar_usuarios import DadosNovoUsuario, GerenciarUsuariosUseCase
from domain.entities.usuario import Administrador
from domain.exceptions import ErroDominio
from infra.config import Configuracao
from infra.db.session import criar_engine, criar_fabrica_sessoes, sessao_transacional
from infra.security import HashScrypt


def criar_administrador(
    fabrica: sessionmaker[Session], hash_de_senha: HashDeSenha, nome: str, email: str, senha: str
) -> Administrador:
    with sessao_transacional(fabrica) as sessao:
        use_case = GerenciarUsuariosUseCase(UsuarioRepositoryPostgres(sessao), hash_de_senha)
        return use_case.criar_primeiro_administrador(DadosNovoUsuario(nome, email, senha))


def main(argumentos: list[str] | None = None) -> int:
    leitor = argparse.ArgumentParser(description="Cria o primeiro administrador do CRM.")
    leitor.add_argument("--nome", required=True)
    leitor.add_argument("--email", required=True)
    opcoes = leitor.parse_args(argumentos)

    senha = getpass.getpass("Senha (mínimo 8 caracteres): ")
    if senha != getpass.getpass("Repita a senha: "):
        print("As senhas não conferem.", file=sys.stderr)
        return 1

    engine = criar_engine(Configuracao().database_url)
    try:
        admin = criar_administrador(
            criar_fabrica_sessoes(engine), HashScrypt(), opcoes.nome, opcoes.email, senha
        )
    except ErroDominio as erro:
        print(f"Não foi possível criar: {erro.mensagem}", file=sys.stderr)
        return 1
    finally:
        engine.dispose()

    print(f"Administrador criado: {admin.nome} <{admin.email.endereco}>")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
