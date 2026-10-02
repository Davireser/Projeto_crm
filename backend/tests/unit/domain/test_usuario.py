"""Usuario e Administrador — herança por perfil (RF10)."""

from uuid import uuid4

import pytest

from domain.entities.usuario import Administrador, Perfil, Usuario
from domain.exceptions import FormatoInvalido, OperacaoNaoPermitida
from domain.value_objects.email import Email

pytestmark = pytest.mark.unit


def usuario() -> Usuario:
    return Usuario(id=uuid4(), nome="Ana", email=Email("ana@crm.com"), senha_hash="hash")


def administrador() -> Administrador:
    return Administrador(id=uuid4(), nome="Admin", email=Email("admin@crm.com"), senha_hash="hash")


def test_usuario_comum_nasce_ativo_com_perfil_usuario() -> None:
    comum = usuario()

    assert comum.ativo
    assert comum.perfil is Perfil.USUARIO


def test_administrador_e_um_usuario_com_perfil_administrador() -> None:
    admin = administrador()

    assert isinstance(admin, Usuario)
    assert admin.perfil is Perfil.ADMINISTRADOR


def test_administrador_desativa_e_reativa_outro_usuario() -> None:
    admin, comum = administrador(), usuario()

    admin.desativar_usuario(comum)
    assert not comum.ativo

    admin.ativar_usuario(comum)
    assert comum.ativo


def test_administrador_nao_pode_desativar_a_propria_conta() -> None:
    admin = administrador()

    with pytest.raises(OperacaoNaoPermitida) as erro:
        admin.desativar_usuario(admin)

    assert erro.value.campo == "ativo"
    assert admin.ativo


@pytest.mark.parametrize("nome", ["", "  "])
def test_usuario_sem_nome_e_rejeitado(nome: str) -> None:
    with pytest.raises(FormatoInvalido):
        Usuario(id=uuid4(), nome=nome, email=Email("a@b.com"), senha_hash="hash")
