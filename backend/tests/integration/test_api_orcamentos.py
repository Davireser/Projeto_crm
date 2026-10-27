"""Rotas do funil: painel, transições, estágio, valor e interações (UC03, UC05-UC07).

Item 7 do plano de TDD: PATCH /orcamentos/{id}/estagio devolve 200 na transição
válida e 422 na inválida.
"""

from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration

URL = "/api/v1"


@pytest.fixture
def orcamento_id(api: TestClient) -> str:
    resposta = api.post(
        f"{URL}/clientes",
        json={"nome": "Maria Souza", "telefone": "31998765432", "email": "maria@x.com"},
    )
    identificador: str = resposta.json()["orcamento"]["id"]
    return identificador


def mover(api: TestClient, orcamento_id: str, estagio: str) -> Any:
    return api.patch(f"{URL}/orcamentos/{orcamento_id}/estagio", json={"estagio": estagio})


def definir_valor(api: TestClient, orcamento_id: str, valor: Any) -> Any:
    return api.patch(f"{URL}/orcamentos/{orcamento_id}/valor", json={"valor": valor})


# --- Painel (UC07) -----------------------------------------------------------


def test_painel_vazio_tem_as_cinco_colunas(api: TestClient) -> None:
    resposta = api.get(f"{URL}/orcamentos")

    assert resposta.status_code == 200
    assert resposta.json() == {
        "NOVO_CONTATO": [],
        "EM_NEGOCIACAO": [],
        "ORCAMENTO_ENVIADO": [],
        "FECHADO": [],
        "PERDIDO": [],
    }


def test_card_do_painel_e_a_projecao_enxuta(api: TestClient, orcamento_id: str) -> None:
    definir_valor(api, orcamento_id, "4200")
    api.post(
        f"{URL}/orcamentos/{orcamento_id}/interacoes", json={"tipo": "MENSAGEM", "conteudo": "Oi"}
    )

    card = api.get(f"{URL}/orcamentos").json()["NOVO_CONTATO"][0]

    assert card == {
        "id": orcamento_id,
        "clienteId": card["clienteId"],
        "clienteNome": "Maria Souza",
        "estagio": "NOVO_CONTATO",
        "valor": "4200.00",
        "dataAbertura": "2026-09-15",
        "qtdInteracoes": 1,
    }


def test_mapa_de_transicoes_para_o_kanban(api: TestClient) -> None:
    resposta = api.get(f"{URL}/orcamentos/transicoes")

    assert resposta.status_code == 200
    assert resposta.json() == {
        "transicoes": {
            "NOVO_CONTATO": ["EM_NEGOCIACAO", "PERDIDO"],
            "EM_NEGOCIACAO": ["ORCAMENTO_ENVIADO", "PERDIDO"],
            "ORCAMENTO_ENVIADO": ["FECHADO", "PERDIDO"],
            "FECHADO": [],
            "PERDIDO": [],
        },
        "exigemValor": ["ORCAMENTO_ENVIADO", "FECHADO"],
    }


# --- Mover estágio (UC03) ----------------------------------------------------


def test_transicao_valida_devolve_200_com_o_orcamento(api: TestClient, orcamento_id: str) -> None:
    resposta = mover(api, orcamento_id, "EM_NEGOCIACAO")

    assert resposta.status_code == 200
    assert resposta.json()["estagio"] == "EM_NEGOCIACAO"
    assert api.get(f"{URL}/orcamentos").json()["EM_NEGOCIACAO"][0]["id"] == orcamento_id


def test_pular_etapa_devolve_422_e_nao_altera_nada(api: TestClient, orcamento_id: str) -> None:
    resposta = mover(api, orcamento_id, "FECHADO")

    assert resposta.status_code == 422
    assert resposta.json() == {
        "erro": "TransicaoInvalida",
        "mensagem": "Não é possível mover de NOVO_CONTATO para FECHADO",
        "campo": "estagio",
    }
    assert api.get(f"{URL}/orcamentos").json()["NOVO_CONTATO"][0]["id"] == orcamento_id


def test_enviar_sem_valor_devolve_422_no_campo_valor(api: TestClient, orcamento_id: str) -> None:
    mover(api, orcamento_id, "EM_NEGOCIACAO")

    resposta = mover(api, orcamento_id, "ORCAMENTO_ENVIADO")

    assert resposta.status_code == 422
    assert resposta.json()["erro"] == "TransicaoInvalida"
    assert resposta.json()["campo"] == "valor"


def test_estagio_desconhecido_devolve_422(api: TestClient, orcamento_id: str) -> None:
    resposta = mover(api, orcamento_id, "QUALQUER")

    assert resposta.status_code == 422
    assert resposta.json()["erro"] == "DadosInvalidos"
    assert resposta.json()["campo"] == "estagio"


def test_mover_orcamento_inexistente_devolve_404(api: TestClient) -> None:
    resposta = mover(api, str(uuid4()), "EM_NEGOCIACAO")

    assert resposta.status_code == 404
    assert resposta.json()["erro"] == "OrcamentoNaoEncontrado"


def test_funil_completo_ate_fechado(api: TestClient, orcamento_id: str) -> None:
    mover(api, orcamento_id, "EM_NEGOCIACAO")
    definir_valor(api, orcamento_id, "4200")
    mover(api, orcamento_id, "ORCAMENTO_ENVIADO")

    resposta = mover(api, orcamento_id, "FECHADO")

    assert resposta.status_code == 200
    assert resposta.json() == {
        "id": orcamento_id,
        "clienteId": resposta.json()["clienteId"],
        "estagio": "FECHADO",
        "valor": "4200.00",
        "dataAbertura": "2026-09-15",
        "dataFechamento": "2026-09-15",
    }


# --- Definir valor (UC05) ----------------------------------------------------


def test_definir_valor_devolve_o_orcamento(api: TestClient, orcamento_id: str) -> None:
    resposta = definir_valor(api, orcamento_id, "1500.5")

    assert resposta.status_code == 200
    assert resposta.json()["valor"] == "1500.50"


@pytest.mark.parametrize("valor", ["0", "-10", "1.999"])
def test_valor_invalido_devolve_422(api: TestClient, orcamento_id: str, valor: str) -> None:
    resposta = definir_valor(api, orcamento_id, valor)

    assert resposta.status_code == 422
    assert resposta.json()["erro"] == "ValorInvalido"
    assert resposta.json()["campo"] == "valor"


def test_valor_que_nao_e_numero_devolve_422(api: TestClient, orcamento_id: str) -> None:
    resposta = definir_valor(api, orcamento_id, "muito")

    assert resposta.status_code == 422
    assert resposta.json()["erro"] == "DadosInvalidos"


# --- Interações (UC06) -------------------------------------------------------


def test_registrar_interacao_devolve_201(api: TestClient, orcamento_id: str) -> None:
    resposta = api.post(
        f"{URL}/orcamentos/{orcamento_id}/interacoes",
        json={"tipo": "LIGACAO", "conteudo": "Pediu 500 caixas"},
    )

    assert resposta.status_code == 201
    assert resposta.json() == {
        "id": resposta.json()["id"],
        "tipo": "LIGACAO",
        "conteudo": "Pediu 500 caixas",
        "dataHora": "2026-09-15T14:30:00Z",
    }


def test_interacao_sem_conteudo_devolve_422(api: TestClient, orcamento_id: str) -> None:
    resposta = api.post(
        f"{URL}/orcamentos/{orcamento_id}/interacoes", json={"tipo": "MENSAGEM", "conteudo": " "}
    )

    assert resposta.status_code == 422
    assert resposta.json()["erro"] == "FormatoInvalido"
    assert resposta.json()["campo"] == "conteudo"


def test_tipo_de_interacao_desconhecido_devolve_422(api: TestClient, orcamento_id: str) -> None:
    resposta = api.post(
        f"{URL}/orcamentos/{orcamento_id}/interacoes", json={"tipo": "EMAIL", "conteudo": "x"}
    )

    assert resposta.status_code == 422
    assert resposta.json()["campo"] == "tipo"


def test_interacao_em_orcamento_inexistente_devolve_404(api: TestClient) -> None:
    resposta = api.post(
        f"{URL}/orcamentos/{uuid4()}/interacoes", json={"tipo": "MENSAGEM", "conteudo": "Oi"}
    )

    assert resposta.status_code == 404
