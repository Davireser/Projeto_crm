"""Login e proteção das rotas (RNF07): sem token válido, nada do CRM responde."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from apoio_api import SENHA, cadastrar, entrar_como, novo_usuario
from domain.entities.usuario import Usuario
from relogio_de_teste import RelogioDeTeste

pytestmark = pytest.mark.integration

URL = "/api/v1"


def test_login_devolve_token_e_usuario(api_anonima: TestClient, admin: Usuario) -> None:
    resposta = api_anonima.post(
        f"{URL}/auth/login", json={"email": "ADMIN@crm.com", "senha": SENHA}
    )

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["tokenType"] == "bearer"
    assert corpo["accessToken"].count(".") == 2  # cabeçalho.conteúdo.assinatura
    assert corpo["expiraEm"] == "2026-09-15T22:30:00Z"  # 8 horas depois
    assert corpo["usuario"] == {
        "id": str(admin.id),
        "nome": "Admin",
        "email": "admin@crm.com",
        "perfil": "ADMINISTRADOR",
        "ativo": True,
    }


def test_token_do_login_abre_as_rotas(api_anonima: TestClient, admin: Usuario) -> None:
    token = api_anonima.post(
        f"{URL}/auth/login", json={"email": "admin@crm.com", "senha": SENHA}
    ).json()["accessToken"]

    resposta = api_anonima.get(f"{URL}/orcamentos", headers={"Authorization": f"Bearer {token}"})

    assert resposta.status_code == 200


@pytest.mark.parametrize(
    ("email", "senha"), [("admin@crm.com", "errada"), ("ninguem@crm.com", SENHA)]
)
def test_login_recusado_devolve_401(
    api_anonima: TestClient, admin: Usuario, email: str, senha: str
) -> None:
    resposta = api_anonima.post(f"{URL}/auth/login", json={"email": email, "senha": senha})

    assert resposta.status_code == 401
    assert resposta.json() == {
        "erro": "CredenciaisInvalidas",
        "mensagem": "E-mail ou senha incorretos.",
        "campo": None,
    }


@pytest.mark.parametrize(
    ("metodo", "rota"),
    [
        ("GET", "/orcamentos"),
        ("GET", "/orcamentos/transicoes"),
        ("POST", "/clientes"),
        ("PATCH", "/orcamentos/00000000-0000-0000-0000-000000000000/estagio"),
        ("GET", "/metricas/funil"),
        ("GET", "/usuarios"),
        ("GET", "/auth/eu"),
    ],
)
def test_rotas_exigem_login(api_anonima: TestClient, metodo: str, rota: str) -> None:
    resposta = api_anonima.request(metodo, f"{URL}{rota}", json={})

    assert resposta.status_code == 401
    assert resposta.json()["erro"] == "NaoAutenticado"
    assert resposta.headers["www-authenticate"] == "Bearer"


def test_token_falsificado_devolve_401(api_anonima: TestClient) -> None:
    resposta = api_anonima.get(f"{URL}/orcamentos", headers={"Authorization": "Bearer abc.def.ghi"})

    assert resposta.status_code == 401


def test_token_expira_depois_de_8_horas(api: TestClient, relogio_api: RelogioDeTeste) -> None:
    assert api.get(f"{URL}/orcamentos").status_code == 200

    relogio_api.avancar(minutos=8 * 60 + 1)

    assert api.get(f"{URL}/orcamentos").status_code == 401


def test_usuario_desativado_perde_o_acesso_na_hora(
    api: TestClient, api_anonima: TestClient, fabrica: sessionmaker[Session]
) -> None:
    ana = cadastrar(fabrica, novo_usuario("Ana", "ana@crm.com"))
    entrar_como(api_anonima, ana)
    assert api_anonima.get(f"{URL}/orcamentos").status_code == 200

    api.patch(f"{URL}/usuarios/{ana.id}", json={"ativo": False})

    assert api_anonima.get(f"{URL}/orcamentos").status_code == 401


def test_quem_sou_eu(api: TestClient, admin: Usuario) -> None:
    resposta = api.get(f"{URL}/auth/eu")

    assert resposta.status_code == 200
    assert resposta.json()["id"] == str(admin.id)


def test_documentacao_continua_publica_e_mostra_o_cadeado(api_anonima: TestClient) -> None:
    assert api_anonima.get("/docs").status_code == 200
    esquema = api_anonima.get("/openapi.json").json()

    assert esquema["components"]["securitySchemes"]["HTTPBearer"]["scheme"] == "bearer"
