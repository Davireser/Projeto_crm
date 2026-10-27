"""Login: confere e-mail e senha (RNF07). Toda falha tem a mesma resposta."""

from uuid import uuid4

import pytest

from adapters.repositories.em_memoria import UsuarioRepositoryEmMemoria
from application.exceptions import CredenciaisInvalidas
from application.use_cases.autenticar_usuario import AutenticarUsuarioUseCase
from domain.entities.usuario import Administrador, Usuario
from domain.value_objects.email import Email
from hash_falso import HashFalso

pytestmark = pytest.mark.unit


@pytest.fixture
def usuarios() -> UsuarioRepositoryEmMemoria:
    repositorio = UsuarioRepositoryEmMemoria()
    repositorio.salvar(
        Usuario(id=uuid4(), nome="Ana", email=Email("ana@crm.com"), senha_hash="hash:segredo123")
    )
    return repositorio


@pytest.fixture
def use_case(usuarios: UsuarioRepositoryEmMemoria) -> AutenticarUsuarioUseCase:
    return AutenticarUsuarioUseCase(usuarios, HashFalso())


def test_credenciais_corretas_devolvem_o_usuario(use_case: AutenticarUsuarioUseCase) -> None:
    usuario = use_case.executar("ANA@crm.com", "segredo123")

    assert usuario.nome == "Ana"


def test_administrador_volta_como_administrador(usuarios: UsuarioRepositoryEmMemoria) -> None:
    usuarios.salvar(
        Administrador(id=uuid4(), nome="Admin", email=Email("adm@crm.com"), senha_hash="hash:x1")
    )

    usuario = AutenticarUsuarioUseCase(usuarios, HashFalso()).executar("adm@crm.com", "x1")

    assert isinstance(usuario, Administrador)


@pytest.mark.parametrize(
    ("email", "senha"),
    [
        ("ana@crm.com", "errada"),  # senha errada
        ("ninguem@crm.com", "segredo123"),  # e-mail desconhecido
        ("nao-e-email", "segredo123"),  # e-mail mal formado
        ("ana@crm.com", ""),  # senha vazia
    ],
)
def test_falhas_de_login_tem_sempre_a_mesma_resposta(
    use_case: AutenticarUsuarioUseCase, email: str, senha: str
) -> None:
    with pytest.raises(CredenciaisInvalidas) as erro:
        use_case.executar(email, senha)

    assert erro.value.mensagem == "E-mail ou senha incorretos."


def test_usuario_desativado_nao_entra(usuarios: UsuarioRepositoryEmMemoria) -> None:
    admin = Administrador(id=uuid4(), nome="Admin", email=Email("adm@crm.com"), senha_hash="h")
    ana = usuarios.buscar_por_email(Email("ana@crm.com"))
    assert ana is not None
    admin.desativar_usuario(ana)
    usuarios.salvar(ana)

    with pytest.raises(CredenciaisInvalidas):
        AutenticarUsuarioUseCase(usuarios, HashFalso()).executar("ana@crm.com", "segredo123")
