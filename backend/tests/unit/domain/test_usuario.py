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


def test_atualizar_cadastro_troca_nome_e_email() -> None:
    ana = usuario()

    ana.atualizar_cadastro(nome="  Ana Lima ", email=Email("ana.lima@crm.com"))

    assert ana.nome == "Ana Lima"
    assert ana.email == Email("ana.lima@crm.com")


def test_atualizar_cadastro_sem_nome_e_rejeitado_sem_alterar_nada() -> None:
    ana = usuario()

    with pytest.raises(FormatoInvalido):
        ana.atualizar_cadastro(nome=" ", email=Email("outro@crm.com"))

    assert ana.nome == "Ana"
    assert ana.email == Email("ana@crm.com")


def test_administrador_promove_usuario_mantendo_os_dados() -> None:
    admin, comum = administrador(), usuario()
    admin.desativar_usuario(comum)

    promovido = admin.definir_perfil(comum, Perfil.ADMINISTRADOR)

    assert isinstance(promovido, Administrador)
    assert (promovido.id, promovido.nome, promovido.email) == (comum.id, comum.nome, comum.email)
    assert promovido.senha_hash == comum.senha_hash
    assert not promovido.ativo


def test_administrador_rebaixa_outro_administrador() -> None:
    admin, outro = administrador(), administrador()

    rebaixado = admin.definir_perfil(outro, Perfil.USUARIO)

    assert type(rebaixado) is Usuario
    assert rebaixado.perfil is Perfil.USUARIO


def test_administrador_nao_pode_alterar_o_proprio_perfil() -> None:
    admin = administrador()

    with pytest.raises(OperacaoNaoPermitida) as erro:
        admin.definir_perfil(admin, Perfil.USUARIO)

    assert erro.value.campo == "perfil"
