"""UC05 — Definir Valor do Orçamento (RF03, RN06)."""

from collections.abc import Callable
from decimal import Decimal
from uuid import uuid4

import pytest

from adapters.repositories.em_memoria import OrcamentoRepositoryEmMemoria
from application.exceptions import OrcamentoNaoEncontrado
from application.relogio import Relogio
from application.use_cases.definir_valor import DefinirValorUseCase
from application.use_cases.mover_estagio import MoverEstagioUseCase
from application.use_cases.registrar_novo_contato import ContatoRegistrado
from domain.exceptions import TransicaoInvalida, ValorInvalido
from domain.value_objects.estagio_atendimento import EstagioAtendimento
from domain.value_objects.valor_orcado import ValorOrcado

pytestmark = pytest.mark.unit


@pytest.fixture
def use_case(orcamentos: OrcamentoRepositoryEmMemoria) -> DefinirValorUseCase:
    return DefinirValorUseCase(orcamentos)


def test_define_e_persiste_o_valor(
    use_case: DefinirValorUseCase,
    orcamentos: OrcamentoRepositoryEmMemoria,
    novo_contato: Callable[..., ContatoRegistrado],
) -> None:
    orcamento_id = novo_contato().orcamento.id

    resultado = use_case.executar(orcamento_id, Decimal("4200"))

    assert resultado.valor == ValorOrcado(Decimal("4200.00"))
    salvo = orcamentos.buscar_por_id(orcamento_id)
    assert salvo is not None
    assert salvo.valor == ValorOrcado(Decimal("4200.00"))


def test_definir_valor_libera_o_envio(
    use_case: DefinirValorUseCase,
    orcamentos: OrcamentoRepositoryEmMemoria,
    relogio: Relogio,
    novo_contato: Callable[..., ContatoRegistrado],
) -> None:
    orcamento_id = novo_contato().orcamento.id
    mover = MoverEstagioUseCase(orcamentos, relogio)
    mover.executar(orcamento_id, EstagioAtendimento.EM_NEGOCIACAO)

    use_case.executar(orcamento_id, Decimal("1500.50"))
    resultado = mover.executar(orcamento_id, EstagioAtendimento.ORCAMENTO_ENVIADO)

    assert resultado.estagio is EstagioAtendimento.ORCAMENTO_ENVIADO


@pytest.mark.parametrize("valor", [Decimal("0"), Decimal("-5"), Decimal("1.999")])
def test_valor_invalido_nao_salva(
    use_case: DefinirValorUseCase,
    orcamentos: OrcamentoRepositoryEmMemoria,
    novo_contato: Callable[..., ContatoRegistrado],
    valor: Decimal,
) -> None:
    orcamento_id = novo_contato().orcamento.id
    salvamentos_antes = orcamentos.salvamentos

    with pytest.raises(ValorInvalido):
        use_case.executar(orcamento_id, valor)

    assert orcamentos.salvamentos == salvamentos_antes


def test_orcamento_encerrado_nao_aceita_valor(
    use_case: DefinirValorUseCase,
    orcamentos: OrcamentoRepositoryEmMemoria,
    relogio: Relogio,
    novo_contato: Callable[..., ContatoRegistrado],
) -> None:
    orcamento_id = novo_contato().orcamento.id
    MoverEstagioUseCase(orcamentos, relogio).executar(orcamento_id, EstagioAtendimento.PERDIDO)
    salvamentos_antes = orcamentos.salvamentos

    with pytest.raises(TransicaoInvalida):
        use_case.executar(orcamento_id, Decimal("100"))

    assert orcamentos.salvamentos == salvamentos_antes


def test_orcamento_inexistente(use_case: DefinirValorUseCase) -> None:
    with pytest.raises(OrcamentoNaoEncontrado):
        use_case.executar(uuid4(), Decimal("100"))
