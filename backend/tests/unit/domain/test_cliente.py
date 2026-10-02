"""Cliente — aggregate root de contato (RF01, RF08, RF09)."""

from datetime import date, datetime

import pytest

from domain.entities.cliente import Cliente
from domain.exceptions import FormatoInvalido
from domain.value_objects.email import Email
from domain.value_objects.estagio_atendimento import EstagioAtendimento
from domain.value_objects.telefone import Telefone

pytestmark = pytest.mark.unit

AGORA = datetime(2026, 9, 1, 9, 0)
HOJE = date(2026, 9, 1)


def cadastrar(nome: str = "Maria Souza") -> Cliente:
    return Cliente.cadastrar(
        nome=nome,
        telefone=Telefone("(31) 99876-5432"),
        email=Email("maria@embalagensabc.com.br"),
        empresa="Embalagens ABC",
        tipo_embalagem_interesse="Caixa de papelão",
        agora=AGORA,
    )


def test_cadastro_guarda_dados_de_contato_validados() -> None:
    cliente = cadastrar()

    assert cliente.nome == "Maria Souza"
    assert cliente.telefone.numero == "31998765432"
    assert cliente.email.endereco == "maria@embalagensabc.com.br"
    assert cliente.empresa == "Embalagens ABC"
    assert cliente.tipo_embalagem_interesse == "Caixa de papelão"
    assert cliente.criado_em == AGORA


def test_empresa_e_tipo_de_embalagem_sao_opcionais() -> None:
    cliente = Cliente.cadastrar(
        nome="João",
        telefone=Telefone("31998765432"),
        email=Email("joao@x.com"),
        agora=AGORA,
    )

    assert cliente.empresa is None
    assert cliente.tipo_embalagem_interesse is None


def test_nome_e_normalizado_sem_espacos_nas_bordas() -> None:
    assert cadastrar("  Maria Souza  ").nome == "Maria Souza"


@pytest.mark.parametrize("nome", ["", "   "])
def test_cliente_sem_nome_e_rejeitado(nome: str) -> None:
    with pytest.raises(FormatoInvalido) as erro:
        cadastrar(nome)
    assert erro.value.campo == "nome"


def test_abrir_orcamento_vincula_ao_cliente_em_novo_contato() -> None:
    cliente = cadastrar()

    orcamento = cliente.abrir_orcamento(hoje=HOJE)

    assert orcamento.cliente_id == cliente.id
    assert orcamento.estagio is EstagioAtendimento.NOVO_CONTATO


def test_cliente_pode_abrir_varios_orcamentos_independentes() -> None:
    cliente = cadastrar()

    primeiro = cliente.abrir_orcamento(hoje=HOJE)
    segundo = cliente.abrir_orcamento(hoje=HOJE)

    assert primeiro.id != segundo.id
    assert primeiro.cliente_id == segundo.cliente_id == cliente.id


def test_atualizar_contato_troca_telefone_e_email() -> None:
    cliente = cadastrar()

    cliente.atualizar_contato(telefone=Telefone("1134567890"), email=Email("novo@x.com"))

    assert cliente.telefone == Telefone("1134567890")
    assert cliente.email == Email("novo@x.com")
