"""Value Objects: validação na construção, imutabilidade e igualdade por valor (RF09, RN04-RN06)."""

import dataclasses
from decimal import Decimal

import pytest

from domain.exceptions import FormatoInvalido, ValorInvalido
from domain.value_objects.email import Email
from domain.value_objects.telefone import Telefone
from domain.value_objects.valor_orcado import ValorOrcado

pytestmark = pytest.mark.unit


# --- Telefone (RN04) ---------------------------------------------------------


@pytest.mark.parametrize(
    ("entrada", "normalizado"),
    [
        ("(31) 99876-5432", "31998765432"),
        ("31998765432", "31998765432"),
        ("(31) 3456-7890", "3134567890"),
        ("11 3456 7890", "1134567890"),
        ("21.99876.5432", "21998765432"),
    ],
)
def test_telefone_valido_e_armazenado_somente_com_digitos(entrada: str, normalizado: str) -> None:
    assert Telefone(entrada).numero == normalizado


@pytest.mark.parametrize(
    "entrada",
    [
        "",
        "99876-5432",  # sem DDD
        "319987654321",  # dígitos demais
        "(01) 99876-5432",  # DDD começando com zero
        "(10) 99876-5432",  # DDD com zero
        "(31) 89876-5432",  # 11 dígitos sem o 9 do celular
        "31abc998765432",  # caracteres fora da máscara
    ],
)
def test_telefone_invalido_nao_chega_a_existir(entrada: str) -> None:
    with pytest.raises(FormatoInvalido) as erro:
        Telefone(entrada)
    assert erro.value.campo == "telefone"


def test_telefone_compara_por_valor() -> None:
    assert Telefone("(31) 99876-5432") == Telefone("31998765432")


# --- Email (RN05) ------------------------------------------------------------


@pytest.mark.parametrize(
    ("entrada", "normalizado"),
    [
        ("contato@embalagensabc.com.br", "contato@embalagensabc.com.br"),
        ("Joao.Silva@Empresa.COM", "joao.silva@empresa.com"),
        ("  vendas+crm@loja-x.com  ", "vendas+crm@loja-x.com"),
    ],
)
def test_email_valido_e_normalizado_para_minusculas(entrada: str, normalizado: str) -> None:
    assert Email(entrada).endereco == normalizado


@pytest.mark.parametrize(
    "entrada",
    ["", "sem-arroba.com", "a@b", "a@@b.com", "@dominio.com", "nome@.com", "nome com espaco@x.com"],
)
def test_email_invalido_nao_chega_a_existir(entrada: str) -> None:
    with pytest.raises(FormatoInvalido) as erro:
        Email(entrada)
    assert erro.value.campo == "email"


# --- ValorOrcado (RN06) ------------------------------------------------------


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    [(Decimal("4200"), "4200.00"), (Decimal("0.01"), "0.01"), (Decimal("99.9"), "99.90")],
)
def test_valor_orcado_positivo_com_duas_casas(entrada: Decimal, esperado: str) -> None:
    assert str(ValorOrcado(entrada).valor) == esperado


@pytest.mark.parametrize(
    "entrada",
    [Decimal("0"), Decimal("-10"), Decimal("10.001"), Decimal("NaN"), Decimal("Infinity")],
)
def test_valor_orcado_invalido_nao_chega_a_existir(entrada: Decimal) -> None:
    with pytest.raises(ValorInvalido) as erro:
        ValorOrcado(entrada)
    assert erro.value.campo == "valor"


def test_valor_orcado_compara_por_valor() -> None:
    assert ValorOrcado(Decimal("10")) == ValorOrcado(Decimal("10.00"))


# --- Imutabilidade -----------------------------------------------------------


def test_value_objects_sao_imutaveis() -> None:
    telefone = Telefone("31998765432")
    with pytest.raises(dataclasses.FrozenInstanceError):
        telefone.numero = "11999999999"  # type: ignore[misc]
