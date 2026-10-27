"""Métricas (UC08), CORS, fuso horário e documentação automática da API."""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient

from apoio_api import entrar_como
from domain.entities.usuario import Usuario
from infra.config import Configuracao
from main import criar_app, relogio_no_fuso
from relogio_de_teste import RelogioDeTeste

pytestmark = pytest.mark.integration

URL = "/api/v1"


def novo_orcamento(api: TestClient, email: str) -> str:
    resposta = api.post(
        f"{URL}/clientes", json={"nome": "Cliente", "telefone": "31998765432", "email": email}
    )
    identificador: str = resposta.json()["orcamento"]["id"]
    return identificador


def test_metricas_de_funil_vazio(api: TestClient) -> None:
    resposta = api.get(f"{URL}/metricas/funil")

    assert resposta.status_code == 200
    assert resposta.json() == {
        "emAberto": 0,
        "fechados": 0,
        "perdidos": 0,
        "taxaFechamento": None,
    }


def test_metricas_contam_abertos_e_calculam_taxa(api: TestClient) -> None:
    aberto = novo_orcamento(api, "a@x.com")
    perdido = novo_orcamento(api, "b@x.com")
    fechado = novo_orcamento(api, "c@x.com")
    api.patch(f"{URL}/orcamentos/{perdido}/estagio", json={"estagio": "PERDIDO"})
    api.patch(f"{URL}/orcamentos/{fechado}/valor", json={"valor": "100"})
    for estagio in ("EM_NEGOCIACAO", "ORCAMENTO_ENVIADO", "FECHADO"):
        api.patch(f"{URL}/orcamentos/{fechado}/estagio", json={"estagio": estagio})

    metricas = api.get(f"{URL}/metricas/funil").json()

    assert aberto
    assert metricas == {
        "emAberto": 1,
        "fechados": 1,
        "perdidos": 1,
        "taxaFechamento": "50.00",
    }


def test_cors_libera_a_origem_do_frontend(api: TestClient) -> None:
    resposta = api.options(
        f"{URL}/orcamentos",
        headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "PATCH"},
    )

    assert resposta.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_cors_recusa_origem_desconhecida(api: TestClient) -> None:
    resposta = api.get(f"{URL}/orcamentos", headers={"Origin": "http://site-estranho.com"})

    assert "access-control-allow-origin" not in resposta.headers


def test_documentacao_openapi_lista_as_rotas(api: TestClient) -> None:
    rotas = api.get("/openapi.json").json()["paths"]

    assert {
        f"{URL}/clientes",
        f"{URL}/clientes/{{cliente_id}}",
        f"{URL}/clientes/{{cliente_id}}/historico",
        f"{URL}/orcamentos",
        f"{URL}/orcamentos/transicoes",
        f"{URL}/orcamentos/{{orcamento_id}}/estagio",
        f"{URL}/orcamentos/{{orcamento_id}}/valor",
        f"{URL}/orcamentos/{{orcamento_id}}/interacoes",
        f"{URL}/metricas/funil",
    } <= set(rotas)


def test_relogio_padrao_usa_o_fuso_do_negocio() -> None:
    agora = relogio_no_fuso("America/Sao_Paulo")()

    assert agora.utcoffset() == timedelta(hours=-3)


def test_data_do_negocio_segue_o_fuso_local_e_horarios_saem_em_utc(
    api: TestClient, relogio_api: RelogioDeTeste, admin: Usuario
) -> None:
    # 22h30 em Brasília já é dia 16 em UTC; o orçamento é do dia 15.
    relogio_api.agora = datetime(2026, 9, 15, 22, 30, tzinfo=ZoneInfo("America/Sao_Paulo"))
    entrar_como(api, admin)  # 11 horas depois, o token anterior já expirou

    corpo = api.post(
        f"{URL}/clientes", json={"nome": "Noturno", "telefone": "31998765432", "email": "n@x.com"}
    ).json()

    assert corpo["orcamento"]["dataAbertura"] == "2026-09-15"
    assert corpo["cliente"]["criadoEm"] == "2026-09-16T01:30:00Z"


def test_producao_recusa_o_segredo_jwt_padrao() -> None:
    with pytest.raises(RuntimeError, match="JWT_SECRET"):
        criar_app(configuracao=Configuracao(_env_file=None, environment="production"))


def test_sem_fabrica_a_conexao_vem_da_configuracao_ao_subir() -> None:
    app = criar_app(configuracao=Configuracao(_env_file=None, database_url="sqlite://"))
    assert app.state.fabrica_sessoes is None  # importar o módulo não abre conexão

    with TestClient(app):
        fabrica = app.state.fabrica_sessoes
        assert fabrica is not None
        assert str(fabrica.kw["bind"].url) == "sqlite://"


ROTAS_COM_CORPO = [
    ("post", "/clientes", "NovoContatoEntrada"),
    ("patch", "/orcamentos/{orcamento_id}/estagio", "MoverEstagioEntrada"),
    ("patch", "/orcamentos/{orcamento_id}/valor", "DefinirValorEntrada"),
    ("post", "/orcamentos/{orcamento_id}/interacoes", "NovaInteracaoEntrada"),
    ("post", "/auth/login", "LoginEntrada"),
    ("post", "/usuarios", "NovoUsuarioEntrada"),
]


def exemplo_documentado(api: TestClient, esquema: str) -> dict[str, object]:
    esquemas = api.get("/openapi.json").json()["components"]["schemas"]
    exemplos = esquemas[esquema].get("examples", [])
    assert exemplos, f"{esquema} sem exemplo: o /docs preencheria tudo com 'string'"
    exemplo: dict[str, object] = exemplos[0]
    return exemplo


@pytest.mark.parametrize(("metodo", "rota", "esquema"), ROTAS_COM_CORPO)
def test_rotas_tem_exemplo_no_docs(api: TestClient, metodo: str, rota: str, esquema: str) -> None:
    assert exemplo_documentado(api, esquema)


def test_exemplo_do_docs_cadastra_cliente_de_verdade(api: TestClient) -> None:
    resposta = api.post(f"{URL}/clientes", json=exemplo_documentado(api, "NovoContatoEntrada"))

    assert resposta.status_code == 201, resposta.text


def test_exemplos_do_docs_percorrem_o_funil(api: TestClient) -> None:
    orcamento = api.post(
        f"{URL}/clientes", json=exemplo_documentado(api, "NovoContatoEntrada")
    ).json()["orcamento"]["id"]
    rota = f"{URL}/orcamentos/{orcamento}"

    assert (
        api.patch(
            f"{rota}/estagio", json=exemplo_documentado(api, "MoverEstagioEntrada")
        ).status_code
        == 200
    )
    assert (
        api.patch(f"{rota}/valor", json=exemplo_documentado(api, "DefinirValorEntrada")).status_code
        == 200
    )
    interacao = exemplo_documentado(api, "NovaInteracaoEntrada")
    assert api.post(f"{rota}/interacoes", json=interacao).status_code == 201
    novo_usuario = exemplo_documentado(api, "NovoUsuarioEntrada")
    assert api.post(f"{URL}/usuarios", json=novo_usuario).status_code == 201
