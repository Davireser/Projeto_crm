"""Fluxo completo do funil pela API, do primeiro contato ao fechamento (doc 12)."""

from collections.abc import Iterator
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from apoio_api import SENHA, cadastrar, montar_app, novo_usuario
from apoio_banco import banco_limpo
from relogio_de_teste import RelogioDeTeste

pytestmark = pytest.mark.e2e

URL = "/api/v1"
AGORA = datetime(2026, 9, 15, 14, 30, tzinfo=UTC)


@pytest.fixture
def relogio() -> RelogioDeTeste:
    return RelogioDeTeste(AGORA)


@pytest.fixture
def api(relogio: RelogioDeTeste) -> Iterator[TestClient]:
    with banco_limpo("sqlite") as fabrica:
        cadastrar(fabrica, novo_usuario("Atendente", "atendente@padaria.com"))
        with TestClient(montar_app(fabrica, relogio)) as cliente:
            yield cliente


def entrar(api: TestClient) -> None:
    """Login de verdade, como o frontend faz; o token vale 8 horas."""
    resposta = api.post(
        f"{URL}/auth/login", json={"email": "atendente@padaria.com", "senha": SENHA}
    )
    assert resposta.status_code == 200, resposta.text
    api.headers["Authorization"] = f"Bearer {resposta.json()['accessToken']}"


def test_do_primeiro_contato_ao_fechamento(api: TestClient, relogio: RelogioDeTeste) -> None:
    # 0. O atendente entra no sistema; sem login, nada funciona.
    assert api.get(f"{URL}/orcamentos").status_code == 401
    entrar(api)

    # 1. Um novo contato chega pelo WhatsApp.
    contato = api.post(
        f"{URL}/clientes",
        json={
            "nome": "Padaria Sol",
            "telefone": "(31) 3456-7890",
            "email": "compras@padariasol.com",
            "tipoEmbalagemInteresse": "Sacos de papel",
        },
    ).json()
    cliente_id, orcamento_id = contato["cliente"]["id"], contato["orcamento"]["id"]
    rota = f"{URL}/orcamentos/{orcamento_id}"

    # 2. No dia seguinte (novo login: o token anterior expirou), a conversa começa.
    relogio.avancar(minutos=24 * 60)
    assert api.get(f"{URL}/orcamentos").status_code == 401
    entrar(api)
    assert api.patch(f"{rota}/estagio", json={"estagio": "EM_NEGOCIACAO"}).status_code == 200
    api.post(f"{rota}/interacoes", json={"tipo": "LIGACAO", "conteudo": "Quer 2 mil sacos"})

    # 3. Tentar enviar sem preço é barrado pelo domínio.
    assert api.patch(f"{rota}/estagio", json={"estagio": "ORCAMENTO_ENVIADO"}).status_code == 422

    # 4. Dias depois, com o preço definido, o orçamento é enviado e fechado.
    relogio.avancar(minutos=3 * 24 * 60)
    entrar(api)
    assert api.patch(f"{rota}/valor", json={"valor": "980.00"}).status_code == 200
    assert api.patch(f"{rota}/estagio", json={"estagio": "ORCAMENTO_ENVIADO"}).status_code == 200
    api.post(f"{rota}/interacoes", json={"tipo": "MENSAGEM", "conteudo": "Aprovado!"})
    fechado = api.patch(f"{rota}/estagio", json={"estagio": "FECHADO"}).json()

    # 5. Painel, métricas e histórico refletem o resultado.
    painel = api.get(f"{URL}/orcamentos").json()
    metricas = api.get(f"{URL}/metricas/funil").json()
    historico = api.get(f"{URL}/clientes/{cliente_id}/historico").json()

    assert fechado["estagio"] == "FECHADO"
    assert fechado["dataAbertura"] == "2026-09-15"
    assert fechado["dataFechamento"] == "2026-09-19"
    assert painel["FECHADO"][0]["qtdInteracoes"] == 2
    assert metricas["taxaFechamento"] == "100.00"
    assert [item["conteudo"] for item in historico] == ["Quer 2 mil sacos", "Aprovado!"]

    # 6. Um orçamento fechado não reabre.
    assert api.patch(f"{rota}/estagio", json={"estagio": "EM_NEGOCIACAO"}).status_code == 422
