"""Transação por requisição: tudo ou nada (decisão 2 da Parte 2, 08-decisao-arquitetura.md).

UC01 faz duas gravações (Cliente e Orçamento). Se a segunda falhar, a primeira
não pode ficar no banco.
"""

from datetime import UTC, datetime

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from adapters.repositories.cliente_repository_postgres import ClienteRepositoryPostgres
from adapters.repositories.orcamento_repository_postgres import OrcamentoRepositoryPostgres
from application.use_cases.registrar_novo_contato import (
    DadosNovoContato,
    RegistrarNovoContatoUseCase,
)
from domain.entities.orcamento import Orcamento
from infra.db.models import ClienteModel, OrcamentoModel
from infra.db.session import sessao_transacional

pytestmark = pytest.mark.integration

AGORA = datetime(2026, 9, 15, 14, 30, tzinfo=UTC)
DADOS = DadosNovoContato(nome="Maria", telefone="31998765432", email="maria@x.com")


class FalhaAoSalvarOrcamento(OrcamentoRepositoryPostgres):
    def salvar(self, orcamento: Orcamento) -> None:
        raise RuntimeError("queda simulada do banco")


def total(sessao: Session, modelo: type[ClienteModel] | type[OrcamentoModel]) -> int:
    return sessao.scalar(select(func.count()).select_from(modelo)) or 0


def test_sucesso_confirma_as_duas_gravacoes(fabrica: sessionmaker[Session]) -> None:
    with sessao_transacional(fabrica) as sessao:
        RegistrarNovoContatoUseCase(
            ClienteRepositoryPostgres(sessao), OrcamentoRepositoryPostgres(sessao), lambda: AGORA
        ).executar(DADOS)

    with fabrica() as nova_sessao:
        assert total(nova_sessao, ClienteModel) == 1
        assert total(nova_sessao, OrcamentoModel) == 1


def test_falha_na_segunda_gravacao_desfaz_a_primeira(fabrica: sessionmaker[Session]) -> None:
    with pytest.raises(RuntimeError), sessao_transacional(fabrica) as sessao:
        RegistrarNovoContatoUseCase(
            ClienteRepositoryPostgres(sessao), FalhaAoSalvarOrcamento(sessao), lambda: AGORA
        ).executar(DADOS)

    with fabrica() as nova_sessao:
        assert total(nova_sessao, ClienteModel) == 0
        assert total(nova_sessao, OrcamentoModel) == 0
