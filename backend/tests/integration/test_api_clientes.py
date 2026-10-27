"""Rotas de cliente: POST /clientes (UC01), GET /clientes/{id} e /historico (UC09)."""

from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from relogio_de_teste import RelogioDeTeste

pytestmark = pytest.mark.integration

URL = "/api/v1"
CONTATO = {
    "nome": "Maria Souza",
    "telefone": "(31) 99876-5432",
    "email": "Maria@EmbalagensABC.com.br",
    "empresa": "Embalagens ABC",
    "tipoEmbalagemInteresse": "Caixa de papelão",
}


def registrar(api: TestClient, **alteracoes: Any) -> dict[str, Any]:
    resposta = api.post(f"{URL}/clientes", json=CONTATO | alteracoes)
    assert resposta.status_code == 201, resposta.text
    corpo: dict[str, Any] = resposta.json()
    return corpo


def test_registrar_contato_cria_cliente_e_orcamento(api: TestClient) -> None:
    corpo = registrar(api)

    assert corpo["cliente"] == {
        "id": corpo["cliente"]["id"],
        "nome": "Maria Souza",
        "telefone": "31998765432",
        "email": "maria@embalagensabc.com.br",
        "empresa": "Embalagens ABC",
        "tipoEmbalagemInteresse": "Caixa de papelão",
        "criadoEm": "2026-09-15T14:30:00Z",
    }
    assert corpo["orcamento"] == {
        "id": corpo["orcamento"]["id"],
        "clienteId": corpo["cliente"]["id"],
        "estagio": "NOVO_CONTATO",
        "valor": None,
        "dataAbertura": "2026-09-15",
        "dataFechamento": None,
    }


def test_campos_opcionais_podem_ser_omitidos(api: TestClient) -> None:
    resposta = api.post(
        f"{URL}/clientes",
        json={"nome": "João", "telefone": "31998765432", "email": "joao@x.com"},
    )

    assert resposta.status_code == 201
    assert resposta.json()["cliente"]["empresa"] is None


@pytest.mark.parametrize(
    ("campo", "valor"), [("telefone", "99876-5432"), ("email", "sem-arroba"), ("nome", " ")]
)
def test_dado_de_contato_invalido_devolve_422_e_nao_cria_nada(
    api: TestClient, campo: str, valor: str
) -> None:
    resposta = api.post(f"{URL}/clientes", json=CONTATO | {campo: valor})

    assert resposta.status_code == 422
    assert resposta.json()["erro"] == "FormatoInvalido"
    assert resposta.json()["campo"] == campo
    assert all(cards == [] for cards in api.get(f"{URL}/orcamentos").json().values())


def test_campo_obrigatorio_ausente_devolve_422_no_formato_padrao(api: TestClient) -> None:
    resposta = api.post(f"{URL}/clientes", json={"nome": "Maria", "telefone": "31998765432"})

    assert resposta.status_code == 422
    assert resposta.json()["erro"] == "DadosInvalidos"
    assert resposta.json()["campo"] == "email"
    assert resposta.json()["mensagem"]


def test_consultar_cliente_com_seus_orcamentos(api: TestClient) -> None:
    contato = registrar(api)
    cliente_id = contato["cliente"]["id"]

    resposta = api.get(f"{URL}/clientes/{cliente_id}")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["nome"] == "Maria Souza"
    assert [o["id"] for o in corpo["orcamentos"]] == [contato["orcamento"]["id"]]


def test_cliente_inexistente_devolve_404(api: TestClient) -> None:
    resposta = api.get(f"{URL}/clientes/{uuid4()}")

    assert resposta.status_code == 404
    assert resposta.json()["erro"] == "ClienteNaoEncontrado"


def test_id_mal_formado_devolve_422(api: TestClient) -> None:
    resposta = api.get(f"{URL}/clientes/nao-e-um-uuid")

    assert resposta.status_code == 422
    assert resposta.json()["erro"] == "DadosInvalidos"


def test_historico_do_cliente_em_ordem_cronologica(
    api: TestClient, relogio_api: RelogioDeTeste
) -> None:
    contato = registrar(api)
    orcamento_id = contato["orcamento"]["id"]
    for tipo, conteudo in (("MENSAGEM", "Oi"), ("LIGACAO", "Retorno")):
        api.post(
            f"{URL}/orcamentos/{orcamento_id}/interacoes",
            json={"tipo": tipo, "conteudo": conteudo},
        )
        relogio_api.avancar(minutos=30)

    resposta = api.get(f"{URL}/clientes/{contato['cliente']['id']}/historico")

    assert resposta.status_code == 200
    itens = resposta.json()
    assert [i["conteudo"] for i in itens] == ["Oi", "Retorno"]
    assert itens[0] == {
        "id": itens[0]["id"],
        "orcamentoId": orcamento_id,
        "tipo": "MENSAGEM",
        "conteudo": "Oi",
        "dataHora": "2026-09-15T14:30:00Z",
    }


def test_historico_de_cliente_inexistente_devolve_404(api: TestClient) -> None:
    assert api.get(f"{URL}/clientes/{uuid4()}/historico").status_code == 404
