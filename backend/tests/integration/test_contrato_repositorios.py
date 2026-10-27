"""Contrato dos repositórios (RNF06, RNF08). Item 6 do plano de TDD.

Cada teste roda contra todas as implementações: em memória, SQLite e — quando
TEST_DATABASE_URL estiver definida — PostgreSQL. Se uma implementação se
comportar diferente das outras, o teste aponta qual.
"""

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest

from apoio_banco import Repositorios
from domain.entities.cliente import Cliente
from domain.entities.usuario import Administrador, Perfil, Usuario
from domain.value_objects.email import Email
from domain.value_objects.estagio_atendimento import EstagioAtendimento
from domain.value_objects.telefone import Telefone
from domain.value_objects.tipo_interacao import TipoInteracao
from domain.value_objects.valor_orcado import ValorOrcado

pytestmark = pytest.mark.integration

AGORA = datetime(2026, 9, 15, 14, 30, tzinfo=UTC)
HOJE = AGORA.date()


def cliente_salvo(repos: Repositorios, nome: str = "Maria") -> Cliente:
    cliente = Cliente.cadastrar(
        nome=nome,
        telefone=Telefone("31998765432"),
        email=Email("maria@x.com"),
        empresa="Embalagens ABC",
        agora=AGORA,
    )
    repos.clientes.salvar(cliente)
    return cliente


# --- Orçamento ---------------------------------------------------------------


def test_orcamento_round_trip_com_interacoes(repos: Repositorios) -> None:
    orcamento = cliente_salvo(repos).abrir_orcamento(hoje=HOJE)
    orcamento.definir_valor(ValorOrcado(Decimal("4200")))
    orcamento.registrar_interacao(TipoInteracao.LIGACAO, "Pediu 500 caixas", agora=AGORA)
    orcamento.registrar_interacao(TipoInteracao.REUNIAO, "Visita", agora=AGORA + timedelta(hours=1))

    repos.orcamentos.salvar(orcamento)
    carregado = repos.orcamentos.buscar_por_id(orcamento.id)

    assert carregado is not None
    assert carregado.cliente_id == orcamento.cliente_id
    assert carregado.estagio is EstagioAtendimento.NOVO_CONTATO
    assert carregado.valor == ValorOrcado(Decimal("4200.00"))
    assert carregado.data_abertura == HOJE
    assert carregado.data_fechamento is None
    assert carregado.interacoes == orcamento.interacoes


def test_orcamento_sem_valor_e_um_estado_valido(repos: Repositorios) -> None:
    orcamento = cliente_salvo(repos).abrir_orcamento(hoje=HOJE)

    repos.orcamentos.salvar(orcamento)

    carregado = repos.orcamentos.buscar_por_id(orcamento.id)
    assert carregado is not None
    assert carregado.valor is None


def test_alteracao_sem_salvar_nao_persiste(repos: Repositorios) -> None:
    orcamento = cliente_salvo(repos).abrir_orcamento(hoje=HOJE)
    repos.orcamentos.salvar(orcamento)

    carregado = repos.orcamentos.buscar_por_id(orcamento.id)
    assert carregado is not None
    carregado.mover_estagio(EstagioAtendimento.EM_NEGOCIACAO, hoje=HOJE)

    de_novo = repos.orcamentos.buscar_por_id(orcamento.id)
    assert de_novo is not None
    assert de_novo.estagio is EstagioAtendimento.NOVO_CONTATO


def test_salvar_de_novo_atualiza_em_vez_de_duplicar(repos: Repositorios) -> None:
    orcamento = cliente_salvo(repos).abrir_orcamento(hoje=HOJE)
    repos.orcamentos.salvar(orcamento)
    orcamento.definir_valor(ValorOrcado(Decimal("900")))
    orcamento.mover_estagio(EstagioAtendimento.PERDIDO, hoje=date(2026, 9, 20))
    orcamento.registrar_interacao(TipoInteracao.MENSAGEM, "Desistiu", agora=AGORA)

    repos.orcamentos.salvar(orcamento)

    assert len(repos.orcamentos.listar_todos()) == 1
    carregado = repos.orcamentos.buscar_por_id(orcamento.id)
    assert carregado is not None
    assert carregado.estagio is EstagioAtendimento.PERDIDO
    assert carregado.valor == ValorOrcado(Decimal("900.00"))
    assert carregado.data_fechamento == date(2026, 9, 20)
    assert len(carregado.interacoes) == 1


def test_buscar_inexistente_devolve_none(repos: Repositorios) -> None:
    assert repos.orcamentos.buscar_por_id(uuid4()) is None
    assert repos.clientes.buscar_por_id(uuid4()) is None
    assert repos.usuarios.buscar_por_id(uuid4()) is None


def test_listar_por_cliente_filtra_pelo_cliente(repos: Repositorios) -> None:
    maria, joao = cliente_salvo(repos, "Maria"), cliente_salvo(repos, "João")
    a1 = maria.abrir_orcamento(hoje=date(2026, 9, 1))
    b1 = joao.abrir_orcamento(hoje=date(2026, 9, 2))
    a2 = maria.abrir_orcamento(hoje=date(2026, 9, 3))
    for orcamento in (a1, b1, a2):
        repos.orcamentos.salvar(orcamento)

    assert {o.id for o in repos.orcamentos.listar_por_cliente(maria.id)} == {a1.id, a2.id}
    assert len(repos.orcamentos.listar_todos()) == 3


# --- Cliente -----------------------------------------------------------------


def test_cliente_round_trip(repos: Repositorios) -> None:
    maria = cliente_salvo(repos)

    carregado = repos.clientes.buscar_por_id(maria.id)

    assert carregado is not None
    assert carregado.nome == "Maria"
    assert carregado.telefone == Telefone("31998765432")
    assert carregado.email == Email("maria@x.com")
    assert carregado.empresa == "Embalagens ABC"
    assert carregado.tipo_embalagem_interesse is None
    assert carregado.criado_em == AGORA


def test_atualizar_cliente(repos: Repositorios) -> None:
    maria = cliente_salvo(repos)
    maria.atualizar_contato(telefone=Telefone("1134567890"), email=Email("nova@x.com"))

    repos.clientes.salvar(maria)

    carregado = repos.clientes.buscar_por_id(maria.id)
    assert carregado is not None
    assert carregado.telefone == Telefone("1134567890")
    assert carregado.email == Email("nova@x.com")


def test_listar_clientes_por_ids_ignora_ids_desconhecidos(repos: Repositorios) -> None:
    maria = cliente_salvo(repos, "Maria")
    cliente_salvo(repos, "João")

    encontrados = repos.clientes.listar_por_ids({maria.id, uuid4()})

    assert [c.id for c in encontrados] == [maria.id]


# --- Usuário -----------------------------------------------------------------


def test_usuario_round_trip_preserva_o_perfil(repos: Repositorios) -> None:
    admin = Administrador(id=uuid4(), nome="Admin", email=Email("admin@crm.com"), senha_hash="h")
    comum = Usuario(
        id=uuid4(), nome="Ana", email=Email("ana@crm.com"), senha_hash="h2", ativo=False
    )
    repos.usuarios.salvar(admin)
    repos.usuarios.salvar(comum)

    carregado_admin = repos.usuarios.buscar_por_id(admin.id)
    carregado_comum = repos.usuarios.buscar_por_id(comum.id)

    assert isinstance(carregado_admin, Administrador)
    assert carregado_admin.perfil is Perfil.ADMINISTRADOR
    assert carregado_comum is not None
    assert type(carregado_comum) is Usuario
    assert carregado_comum.senha_hash == "h2"
    assert not carregado_comum.ativo
    assert len(repos.usuarios.listar_todos()) == 2


def test_salvar_usuario_de_novo_atualiza(repos: Repositorios) -> None:
    admin = Administrador(id=uuid4(), nome="Admin", email=Email("admin@crm.com"), senha_hash="h")
    comum = Usuario(id=uuid4(), nome="Ana", email=Email("ana@crm.com"), senha_hash="h")
    repos.usuarios.salvar(admin)
    repos.usuarios.salvar(comum)

    admin.desativar_usuario(comum)
    repos.usuarios.salvar(comum)

    carregado = repos.usuarios.buscar_por_id(comum.id)
    assert carregado is not None
    assert not carregado.ativo
    assert len(repos.usuarios.listar_todos()) == 2


def test_buscar_usuario_por_email(repos: Repositorios) -> None:
    ana = Usuario(id=uuid4(), nome="Ana", email=Email("ana@crm.com"), senha_hash="h")
    repos.usuarios.salvar(ana)

    encontrado = repos.usuarios.buscar_por_email(Email("ANA@crm.com"))

    assert encontrado is not None
    assert encontrado.id == ana.id
    assert repos.usuarios.buscar_por_email(Email("outro@crm.com")) is None
