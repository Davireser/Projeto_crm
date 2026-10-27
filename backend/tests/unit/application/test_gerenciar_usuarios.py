"""UC10 — Gerenciar Usuários (RF10, RNF07): só Administrador cria, edita e desativa."""

from uuid import uuid4

import pytest

from adapters.repositories.em_memoria import UsuarioRepositoryEmMemoria
from application.exceptions import AcessoNegado, EmailJaCadastrado, UsuarioNaoEncontrado
from application.use_cases.gerenciar_usuarios import (
    DadosEdicaoUsuario,
    DadosNovoUsuario,
    GerenciarUsuariosUseCase,
)
from domain.entities.usuario import Administrador, Perfil, Usuario
from domain.exceptions import FormatoInvalido, OperacaoNaoPermitida
from domain.value_objects.email import Email
from hash_falso import HashFalso

pytestmark = pytest.mark.unit


@pytest.fixture
def usuarios() -> UsuarioRepositoryEmMemoria:
    return UsuarioRepositoryEmMemoria()


@pytest.fixture
def use_case(usuarios: UsuarioRepositoryEmMemoria) -> GerenciarUsuariosUseCase:
    return GerenciarUsuariosUseCase(usuarios, HashFalso())


@pytest.fixture
def admin(usuarios: UsuarioRepositoryEmMemoria) -> Administrador:
    administrador = Administrador(
        id=uuid4(), nome="Admin", email=Email("admin@crm.com"), senha_hash="hash:admin1234"
    )
    usuarios.salvar(administrador)
    return administrador


@pytest.fixture
def ana(usuarios: UsuarioRepositoryEmMemoria) -> Usuario:
    comum = Usuario(id=uuid4(), nome="Ana", email=Email("ana@crm.com"), senha_hash="hash:ana12345")
    usuarios.salvar(comum)
    return comum


# --- Autorização (RNF07) -----------------------------------------------------


def test_usuario_comum_nao_gerencia_usuarios(
    use_case: GerenciarUsuariosUseCase, ana: Usuario
) -> None:
    with pytest.raises(AcessoNegado):
        use_case.listar(ana)
    with pytest.raises(AcessoNegado):
        use_case.criar(ana, DadosNovoUsuario(nome="X", email="x@crm.com", senha="12345678"))
    with pytest.raises(AcessoNegado):
        use_case.editar(ana, ana.id, DadosEdicaoUsuario(nome="Outro nome"))


# --- Listar e criar ----------------------------------------------------------


def test_administrador_lista_todos(
    use_case: GerenciarUsuariosUseCase, admin: Administrador, ana: Usuario
) -> None:
    assert {u.id for u in use_case.listar(admin)} == {admin.id, ana.id}


def test_criar_usuario_guarda_so_o_hash_da_senha(
    use_case: GerenciarUsuariosUseCase, admin: Administrador, usuarios: UsuarioRepositoryEmMemoria
) -> None:
    criado = use_case.criar(
        admin, DadosNovoUsuario(nome="Bruno", email="Bruno@CRM.com", senha="senha-forte")
    )

    salvo = usuarios.buscar_por_id(criado.id)
    assert salvo is not None
    assert salvo.email == Email("bruno@crm.com")
    assert salvo.senha_hash == "hash:senha-forte"
    assert salvo.perfil is Perfil.USUARIO
    assert salvo.ativo


def test_criar_administrador(use_case: GerenciarUsuariosUseCase, admin: Administrador) -> None:
    criado = use_case.criar(
        admin,
        DadosNovoUsuario(
            nome="Carla", email="carla@crm.com", senha="senha-forte", perfil=Perfil.ADMINISTRADOR
        ),
    )

    assert isinstance(criado, Administrador)


def test_senha_curta_e_rejeitada(
    use_case: GerenciarUsuariosUseCase, admin: Administrador, usuarios: UsuarioRepositoryEmMemoria
) -> None:
    salvamentos = usuarios.salvamentos

    with pytest.raises(FormatoInvalido) as erro:
        use_case.criar(admin, DadosNovoUsuario(nome="Bruno", email="b@crm.com", senha="1234567"))

    assert erro.value.campo == "senha"
    assert usuarios.salvamentos == salvamentos


def test_email_repetido_e_rejeitado(
    use_case: GerenciarUsuariosUseCase, admin: Administrador, ana: Usuario
) -> None:
    with pytest.raises(EmailJaCadastrado) as erro:
        use_case.criar(admin, DadosNovoUsuario(nome="Outra", email="ANA@crm.com", senha="12345678"))

    assert erro.value.campo == "email"


# --- Editar ------------------------------------------------------------------


def test_editar_nome_e_email(
    use_case: GerenciarUsuariosUseCase, admin: Administrador, ana: Usuario
) -> None:
    editado = use_case.editar(
        admin, ana.id, DadosEdicaoUsuario(nome="Ana Lima", email="ana.lima@crm.com")
    )

    assert editado.nome == "Ana Lima"
    assert editado.email == Email("ana.lima@crm.com")


def test_campos_omitidos_ficam_como_estavam(
    use_case: GerenciarUsuariosUseCase, admin: Administrador, ana: Usuario
) -> None:
    editado = use_case.editar(admin, ana.id, DadosEdicaoUsuario(nome="Ana Lima"))

    assert editado.email == Email("ana@crm.com")
    assert editado.ativo


def test_desativar_e_reativar_outro_usuario(
    use_case: GerenciarUsuariosUseCase, admin: Administrador, ana: Usuario
) -> None:
    assert not use_case.editar(admin, ana.id, DadosEdicaoUsuario(ativo=False)).ativo
    assert use_case.editar(admin, ana.id, DadosEdicaoUsuario(ativo=True)).ativo


def test_administrador_nao_se_desativa(
    use_case: GerenciarUsuariosUseCase, admin: Administrador
) -> None:
    with pytest.raises(OperacaoNaoPermitida):
        use_case.editar(admin, admin.id, DadosEdicaoUsuario(ativo=False))


def test_promover_usuario_a_administrador(
    use_case: GerenciarUsuariosUseCase,
    admin: Administrador,
    ana: Usuario,
    usuarios: UsuarioRepositoryEmMemoria,
) -> None:
    use_case.editar(admin, ana.id, DadosEdicaoUsuario(perfil=Perfil.ADMINISTRADOR))

    assert isinstance(usuarios.buscar_por_id(ana.id), Administrador)


def test_email_de_outro_usuario_e_rejeitado_na_edicao(
    use_case: GerenciarUsuariosUseCase, admin: Administrador, ana: Usuario
) -> None:
    with pytest.raises(EmailJaCadastrado):
        use_case.editar(admin, ana.id, DadosEdicaoUsuario(email="admin@crm.com"))


def test_manter_o_proprio_email_nao_e_conflito(
    use_case: GerenciarUsuariosUseCase, admin: Administrador, ana: Usuario
) -> None:
    editado = use_case.editar(admin, ana.id, DadosEdicaoUsuario(email="ANA@crm.com"))

    assert editado.email == Email("ana@crm.com")


def test_editar_usuario_inexistente(
    use_case: GerenciarUsuariosUseCase, admin: Administrador
) -> None:
    with pytest.raises(UsuarioNaoEncontrado):
        use_case.editar(admin, uuid4(), DadosEdicaoUsuario(nome="X"))


# --- Primeiro administrador --------------------------------------------------


def test_primeiro_administrador_so_quando_nao_ha_usuarios(
    use_case: GerenciarUsuariosUseCase, usuarios: UsuarioRepositoryEmMemoria
) -> None:
    primeiro = use_case.criar_primeiro_administrador(
        DadosNovoUsuario(nome="Dona", email="dona@crm.com", senha="senha-forte")
    )

    assert isinstance(primeiro, Administrador)
    with pytest.raises(OperacaoNaoPermitida):
        use_case.criar_primeiro_administrador(
            DadosNovoUsuario(nome="Outro", email="outro@crm.com", senha="senha-forte")
        )
    assert len(usuarios.listar_todos()) == 1
