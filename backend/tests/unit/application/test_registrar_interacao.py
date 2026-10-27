"""UC06 — Registrar Interação (RF04). A interação entra pelo agregado Orcamento."""

from collections.abc import Callable
from datetime import datetime
from uuid import uuid4

import pytest

from adapters.repositories.em_memoria import OrcamentoRepositoryEmMemoria
from application.exceptions import OrcamentoNaoEncontrado
from application.relogio import Relogio
from application.use_cases.registrar_interacao import RegistrarInteracaoUseCase
from application.use_cases.registrar_novo_contato import ContatoRegistrado
from domain.exceptions import FormatoInvalido
from domain.value_objects.tipo_interacao import TipoInteracao

pytestmark = pytest.mark.unit


@pytest.fixture
def use_case(
    orcamentos: OrcamentoRepositoryEmMemoria, relogio: Relogio
) -> RegistrarInteracaoUseCase:
    return RegistrarInteracaoUseCase(orcamentos, relogio)


def test_registra_com_data_e_hora_do_sistema(
    use_case: RegistrarInteracaoUseCase,
    orcamentos: OrcamentoRepositoryEmMemoria,
    novo_contato: Callable[..., ContatoRegistrado],
    agora: datetime,
) -> None:
    orcamento_id = novo_contato().orcamento.id

    interacao = use_case.executar(orcamento_id, TipoInteracao.LIGACAO, "Pediu 500 caixas")

    assert interacao.data_hora == agora
    salvo = orcamentos.buscar_por_id(orcamento_id)
    assert salvo is not None
    assert salvo.interacoes == (interacao,)


def test_conteudo_vazio_nao_salva(
    use_case: RegistrarInteracaoUseCase,
    orcamentos: OrcamentoRepositoryEmMemoria,
    novo_contato: Callable[..., ContatoRegistrado],
) -> None:
    orcamento_id = novo_contato().orcamento.id
    salvamentos_antes = orcamentos.salvamentos

    with pytest.raises(FormatoInvalido):
        use_case.executar(orcamento_id, TipoInteracao.MENSAGEM, "  ")

    assert orcamentos.salvamentos == salvamentos_antes


def test_orcamento_inexistente(use_case: RegistrarInteracaoUseCase) -> None:
    with pytest.raises(OrcamentoNaoEncontrado):
        use_case.executar(uuid4(), TipoInteracao.MENSAGEM, "Oi")
