"""RNF01: o painel carrega em menos de 2 segundos com 500 orçamentos ativos."""

import time
from datetime import UTC, date, datetime, timedelta
from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import insert
from sqlalchemy.orm import Session, sessionmaker

from infra.db.models import ClienteModel, InteracaoModel, OrcamentoModel
from infra.db.session import sessao_transacional

pytestmark = pytest.mark.integration

QUANTIDADE = 500
INTERACOES_POR_ORCAMENTO = 3
LIMITE_EM_SEGUNDOS = 2.0
AGORA = datetime(2026, 9, 15, 14, 30, tzinfo=UTC)


def popular(fabrica: sessionmaker[Session]) -> None:
    """Insere os dados em lote — uma consulta por tabela.

    Inserir um por um levaria minutos num banco remoto (cada linha é uma ida e
    volta pela rede); o que se mede aqui é a leitura do painel, não a carga.
    """
    clientes: list[dict[str, Any]] = []
    orcamentos: list[dict[str, Any]] = []
    interacoes: list[dict[str, Any]] = []
    for i in range(QUANTIDADE):
        cliente_id, orcamento_id = uuid4(), uuid4()
        clientes.append(
            {
                "id": cliente_id,
                "nome": f"Cliente {i:03d}",
                "telefone": "31998765432",
                "email": f"cliente{i}@x.com",
                "criado_em": AGORA,
            }
        )
        orcamentos.append(
            {
                "id": orcamento_id,
                "cliente_id": cliente_id,
                "estagio": "EM_NEGOCIACAO" if i % 2 else "NOVO_CONTATO",
                "data_abertura": date(2026, 9, 1) + timedelta(days=i % 14),
            }
        )
        interacoes.extend(
            {
                "id": uuid4(),
                "orcamento_id": orcamento_id,
                "tipo": "MENSAGEM",
                "conteudo": "Contato",
                "data_hora": AGORA + timedelta(minutes=minuto),
            }
            for minuto in range(INTERACOES_POR_ORCAMENTO)
        )

    with sessao_transacional(fabrica) as sessao:
        sessao.execute(insert(ClienteModel).values(clientes))
        sessao.execute(insert(OrcamentoModel).values(orcamentos))
        sessao.execute(insert(InteracaoModel).values(interacoes))


def test_painel_com_500_orcamentos_em_menos_de_2_segundos(
    api: TestClient, fabrica: sessionmaker[Session]
) -> None:
    popular(fabrica)

    inicio = time.perf_counter()
    resposta = api.get("/api/v1/orcamentos")
    duracao = time.perf_counter() - inicio

    painel = resposta.json()
    assert resposta.status_code == 200
    assert sum(len(cards) for cards in painel.values()) == QUANTIDADE
    assert painel["EM_NEGOCIACAO"][0]["qtdInteracoes"] == INTERACOES_POR_ORCAMENTO
    assert duracao < LIMITE_EM_SEGUNDOS, f"painel levou {duracao:.2f}s"
