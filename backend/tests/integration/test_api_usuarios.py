"""Rotas de usuários — UC10 (RF10): só Administrador."""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from apoio_api import cadastrar, entrar_como, novo_usuario
from domain.entities.usuario import Usuario

pytestmark = pytest.mark.integration

URL = "/api/v1"
NOVO = {"nome": "Bruno", "email": "bruno@crm.com", "senha": "senha-forte-123"}


@pytest.fixture
def ana(fabrica: sessionmaker[Session]) -> Usuario:
    return cadastrar(fabrica, novo_usuario("Ana", "ana@crm.com"))


def test_administrador_lista_usuarios(api: TestClient, ana: Usuario) -> None:
    resposta = api.get(f"{URL}/usuarios")

    assert resposta.status_code == 200
    assert {u["email"] for u in resposta.json()} == {"admin@crm.com", "ana@crm.com"}


def test_resposta_nunca_expoe_a_senha(api: TestClient, ana: Usuario) -> None:
    texto = api.get(f"{URL}/usuarios").text + api.post(f"{URL}/usuarios", json=NOVO).text

    assert "senha" not in texto.lower()
    assert "scrypt" not in texto


def test_criar_usuario_que_ja_consegue_entrar(api: TestClient, api_anonima: TestClient) -> None:
    resposta = api.post(f"{URL}/usuarios", json=NOVO)

    assert resposta.status_code == 201
    assert resposta.json()["perfil"] == "USUARIO"
    login = api_anonima.post(
        f"{URL}/auth/login", json={"email": "bruno@crm.com", "senha": "senha-forte-123"}
    )
    assert login.status_code == 200


def test_senha_curta_devolve_422(api: TestClient) -> None:
    resposta = api.post(f"{URL}/usuarios", json=NOVO | {"senha": "curta"})

    assert resposta.status_code == 422
    assert resposta.json()["campo"] == "senha"


def test_email_repetido_devolve_409(api: TestClient, ana: Usuario) -> None:
    resposta = api.post(f"{URL}/usuarios", json=NOVO | {"email": "ana@crm.com"})

    assert resposta.status_code == 409
    assert resposta.json()["erro"] == "EmailJaCadastrado"
    assert resposta.json()["campo"] == "email"


def test_editar_e_desativar_outro_usuario(api: TestClient, ana: Usuario) -> None:
    resposta = api.patch(f"{URL}/usuarios/{ana.id}", json={"nome": "Ana Lima", "ativo": False})

    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "Ana Lima"
    assert resposta.json()["ativo"] is False


def test_promover_a_administrador(api: TestClient, ana: Usuario) -> None:
    resposta = api.patch(f"{URL}/usuarios/{ana.id}", json={"perfil": "ADMINISTRADOR"})

    assert resposta.json()["perfil"] == "ADMINISTRADOR"


def test_auto_desativacao_devolve_422(api: TestClient, admin: Usuario) -> None:
    resposta = api.patch(f"{URL}/usuarios/{admin.id}", json={"ativo": False})

    assert resposta.status_code == 422
    assert resposta.json()["erro"] == "OperacaoNaoPermitida"


def test_editar_usuario_inexistente_devolve_404(api: TestClient) -> None:
    resposta = api.patch(f"{URL}/usuarios/{uuid4()}", json={"nome": "X"})

    assert resposta.status_code == 404
    assert resposta.json()["erro"] == "UsuarioNaoEncontrado"


@pytest.mark.parametrize(
    ("metodo", "rota", "corpo"),
    [
        ("GET", "/usuarios", None),
        ("POST", "/usuarios", NOVO),
        ("PATCH", "/usuarios/{ana}", {"nome": "Invasão"}),
    ],
)
def test_usuario_comum_recebe_403(
    api_anonima: TestClient, ana: Usuario, metodo: str, rota: str, corpo: object
) -> None:
    entrar_como(api_anonima, ana)

    resposta = api_anonima.request(metodo, URL + rota.format(ana=ana.id), json=corpo)

    assert resposta.status_code == 403
    assert resposta.json()["erro"] == "AcessoNegado"


def test_usuario_comum_usa_o_crm_normalmente(api_anonima: TestClient, ana: Usuario) -> None:
    entrar_como(api_anonima, ana)

    assert api_anonima.get(f"{URL}/orcamentos").status_code == 200
