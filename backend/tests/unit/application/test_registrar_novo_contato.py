"""UC01 — Registrar Novo Contato (RF01, RF09). Item 4 do plano de TDD."""

from datetime import datetime

import pytest

from adapters.repositories.em_memoria import (
    ClienteRepositoryEmMemoria,
    OrcamentoRepositoryEmMemoria,
)
from application.relogio import Relogio
from application.use_cases.registrar_novo_contato import (
    DadosNovoContato,
    RegistrarNovoContatoUseCase,
)
from domain.exceptions import FormatoInvalido
from domain.value_objects.estagio_atendimento import EstagioAtendimento

pytestmark = pytest.mark.unit


@pytest.fixture
def use_case(
    clientes: ClienteRepositoryEmMemoria,
    orcamentos: OrcamentoRepositoryEmMemoria,
    relogio: Relogio,
) -> RegistrarNovoContatoUseCase:
    return RegistrarNovoContatoUseCase(clientes, orcamentos, relogio)


def dados(**alteracoes: str) -> DadosNovoContato:
    campos = {
        "nome": "Maria Souza",
        "telefone": "(31) 99876-5432",
        "email": "maria@embalagensabc.com.br",
        "empresa": "Embalagens ABC",
        "tipo_embalagem_interesse": "Caixa de papelão",
    } | alteracoes
    return DadosNovoContato(**campos)


def test_cria_cliente_e_orcamento_em_novo_contato(
    use_case: RegistrarNovoContatoUseCase,
    clientes: ClienteRepositoryEmMemoria,
    orcamentos: OrcamentoRepositoryEmMemoria,
    agora: datetime,
) -> None:
    resultado = use_case.executar(dados())

    cliente = clientes.buscar_por_id(resultado.cliente.id)
    orcamento = orcamentos.buscar_por_id(resultado.orcamento.id)
    assert cliente is not None
    assert orcamento is not None
    assert cliente.nome == "Maria Souza"
    assert cliente.telefone.numero == "31998765432"
    assert cliente.empresa == "Embalagens ABC"
    assert cliente.criado_em == agora
    assert orcamento.cliente_id == cliente.id
    assert orcamento.estagio is EstagioAtendimento.NOVO_CONTATO
    assert orcamento.data_abertura == agora.date()


def test_empresa_e_tipo_de_embalagem_sao_opcionais(use_case: RegistrarNovoContatoUseCase) -> None:
    resultado = use_case.executar(
        DadosNovoContato(nome="João", telefone="31998765432", email="joao@x.com")
    )

    assert resultado.cliente.empresa is None
    assert resultado.cliente.tipo_embalagem_interesse is None


@pytest.mark.parametrize(
    ("campo", "valor_invalido"),
    [("telefone", "99876-5432"), ("email", "sem-arroba.com"), ("nome", "   ")],
)
def test_dado_invalido_nao_persiste_nada(
    use_case: RegistrarNovoContatoUseCase,
    clientes: ClienteRepositoryEmMemoria,
    orcamentos: OrcamentoRepositoryEmMemoria,
    campo: str,
    valor_invalido: str,
) -> None:
    with pytest.raises(FormatoInvalido) as erro:
        use_case.executar(dados(**{campo: valor_invalido}))

    assert erro.value.campo == campo
    assert clientes.salvamentos == 0
    assert orcamentos.salvamentos == 0
