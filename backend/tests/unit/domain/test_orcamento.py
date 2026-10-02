"""Orcamento — aggregate root do funil (RF02, RF03, RF04, RN01-RN03).

Primeiro teste do plano de TDD: a máquina de estados inteira é exercitada aqui,
sem banco e sem framework.
"""

import itertools
from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from domain.entities.orcamento import Orcamento
from domain.exceptions import FormatoInvalido, TransicaoInvalida
from domain.value_objects.estagio_atendimento import TRANSICOES_PERMITIDAS, EstagioAtendimento
from domain.value_objects.tipo_interacao import TipoInteracao
from domain.value_objects.valor_orcado import ValorOrcado

pytestmark = pytest.mark.unit

E = EstagioAtendimento
ABERTURA = date(2026, 9, 1)
HOJE = date(2026, 9, 15)
AGORA = datetime(2026, 9, 15, 14, 30)
VALOR = ValorOrcado(Decimal("4200.00"))

# Caminho até cada estágio a partir de NOVO_CONTATO.
CAMINHO: dict[EstagioAtendimento, list[EstagioAtendimento]] = {
    E.NOVO_CONTATO: [],
    E.EM_NEGOCIACAO: [E.EM_NEGOCIACAO],
    E.ORCAMENTO_ENVIADO: [E.EM_NEGOCIACAO, E.ORCAMENTO_ENVIADO],
    E.FECHADO: [E.EM_NEGOCIACAO, E.ORCAMENTO_ENVIADO, E.FECHADO],
    E.PERDIDO: [E.PERDIDO],
}


def novo_orcamento() -> Orcamento:
    return Orcamento.abrir(cliente_id=uuid4(), hoje=ABERTURA)


def orcamento_em(estagio: EstagioAtendimento, *, com_valor: bool = True) -> Orcamento:
    orcamento = novo_orcamento()
    if com_valor:
        orcamento.definir_valor(VALOR)
    for passo in CAMINHO[estagio]:
        orcamento.mover_estagio(passo, hoje=HOJE)
    return orcamento


# --- Abertura ----------------------------------------------------------------


def test_orcamento_nasce_em_novo_contato_sem_valor_e_sem_fechamento() -> None:
    cliente_id = uuid4()
    orcamento = Orcamento.abrir(cliente_id=cliente_id, hoje=ABERTURA)

    assert orcamento.cliente_id == cliente_id
    assert orcamento.estagio is E.NOVO_CONTATO
    assert orcamento.valor is None
    assert orcamento.data_abertura == ABERTURA
    assert orcamento.data_fechamento is None
    assert orcamento.interacoes == ()
    assert orcamento.esta_em_aberto()


def test_cada_orcamento_tem_identidade_propria() -> None:
    assert novo_orcamento().id != novo_orcamento().id


# --- Máquina de estados: todos os 25 pares (RF02 / RN01) ---------------------

TODOS_OS_PARES = list(itertools.product(E, E))
PARES_PERMITIDOS = [(o, d) for o, d in TODOS_OS_PARES if d in TRANSICOES_PERMITIDAS[o]]
PARES_PROIBIDOS = [(o, d) for o, d in TODOS_OS_PARES if d not in TRANSICOES_PERMITIDAS[o]]


def test_pares_cobrem_toda_a_matriz() -> None:
    assert len(PARES_PERMITIDOS) == 6
    assert len(PARES_PROIBIDOS) == 19


@pytest.mark.parametrize(("origem", "destino"), PARES_PERMITIDOS)
def test_transicao_permitida_altera_o_estagio(
    origem: EstagioAtendimento, destino: EstagioAtendimento
) -> None:
    orcamento = orcamento_em(origem)

    orcamento.mover_estagio(destino, hoje=HOJE)

    assert orcamento.estagio is destino


@pytest.mark.parametrize(("origem", "destino"), PARES_PROIBIDOS)
def test_transicao_proibida_e_rejeitada_sem_alterar_estado(
    origem: EstagioAtendimento, destino: EstagioAtendimento
) -> None:
    orcamento = orcamento_em(origem)
    data_fechamento_antes = orcamento.data_fechamento

    with pytest.raises(TransicaoInvalida) as erro:
        orcamento.mover_estagio(destino, hoje=HOJE)

    assert erro.value.campo == "estagio"
    assert orcamento.estagio is origem
    assert orcamento.data_fechamento == data_fechamento_antes


def test_salto_de_etapa_tem_mensagem_clara() -> None:
    with pytest.raises(TransicaoInvalida, match="NOVO_CONTATO para FECHADO"):
        novo_orcamento().mover_estagio(E.FECHADO, hoje=HOJE)


# --- Guarda [valorDefinido] (RF03 / RN02) ------------------------------------


def test_nao_envia_orcamento_sem_valor() -> None:
    orcamento = orcamento_em(E.EM_NEGOCIACAO, com_valor=False)

    with pytest.raises(TransicaoInvalida) as erro:
        orcamento.mover_estagio(E.ORCAMENTO_ENVIADO, hoje=HOJE)

    assert erro.value.campo == "valor"
    assert orcamento.estagio is E.EM_NEGOCIACAO


def test_definir_valor_libera_a_transicao_guardada() -> None:
    orcamento = orcamento_em(E.EM_NEGOCIACAO, com_valor=False)

    orcamento.definir_valor(VALOR)
    orcamento.mover_estagio(E.ORCAMENTO_ENVIADO, hoje=HOJE)

    assert orcamento.estagio is E.ORCAMENTO_ENVIADO


def test_nao_fecha_orcamento_sem_valor() -> None:
    # Estado só alcançável por reconstituição (ex.: dado legado no banco).
    orcamento = Orcamento(
        id=uuid4(),
        cliente_id=uuid4(),
        estagio=E.ORCAMENTO_ENVIADO,
        valor=None,
        data_abertura=ABERTURA,
    )

    with pytest.raises(TransicaoInvalida) as erro:
        orcamento.mover_estagio(E.FECHADO, hoje=HOJE)

    assert erro.value.campo == "valor"
    assert orcamento.estagio is E.ORCAMENTO_ENVIADO
    assert orcamento.data_fechamento is None


def test_marcar_perdido_nao_exige_valor() -> None:
    orcamento = orcamento_em(E.EM_NEGOCIACAO, com_valor=False)

    orcamento.mover_estagio(E.PERDIDO, hoje=HOJE)

    assert orcamento.estagio is E.PERDIDO


# --- Data de fechamento (RN03) -----------------------------------------------


@pytest.mark.parametrize("terminal", [E.FECHADO, E.PERDIDO])
def test_entrar_em_estagio_terminal_preenche_data_de_fechamento(
    terminal: EstagioAtendimento,
) -> None:
    orcamento = orcamento_em(terminal)

    assert orcamento.data_fechamento == HOJE
    assert not orcamento.esta_em_aberto()


@pytest.mark.parametrize("ativo", [E.NOVO_CONTATO, E.EM_NEGOCIACAO, E.ORCAMENTO_ENVIADO])
def test_estagios_ativos_nao_tem_data_de_fechamento(ativo: EstagioAtendimento) -> None:
    orcamento = orcamento_em(ativo)

    assert orcamento.data_fechamento is None
    assert orcamento.esta_em_aberto()


# --- Definir valor -----------------------------------------------------------


def test_valor_pode_ser_alterado_enquanto_aberto() -> None:
    orcamento = orcamento_em(E.ORCAMENTO_ENVIADO)
    novo_valor = ValorOrcado(Decimal("3900.00"))

    orcamento.definir_valor(novo_valor)

    assert orcamento.valor == novo_valor


@pytest.mark.parametrize("terminal", [E.FECHADO, E.PERDIDO])
def test_valor_nao_pode_ser_alterado_apos_encerramento(terminal: EstagioAtendimento) -> None:
    orcamento = orcamento_em(terminal)

    with pytest.raises(TransicaoInvalida) as erro:
        orcamento.definir_valor(ValorOrcado(Decimal("1.00")))

    assert erro.value.campo == "valor"
    assert orcamento.valor == VALOR


# --- Interações (RF04) -------------------------------------------------------


def test_registrar_interacao_adiciona_ao_agregado() -> None:
    orcamento = novo_orcamento()

    interacao = orcamento.registrar_interacao(
        TipoInteracao.LIGACAO, "Cliente pediu 500 caixas", agora=AGORA
    )

    assert orcamento.interacoes == (interacao,)
    assert interacao.tipo is TipoInteracao.LIGACAO
    assert interacao.conteudo == "Cliente pediu 500 caixas"
    assert interacao.data_hora == AGORA


def test_interacoes_preservam_ordem_de_registro() -> None:
    orcamento = novo_orcamento()
    primeira = orcamento.registrar_interacao(TipoInteracao.MENSAGEM, "Oi", agora=AGORA)
    segunda = orcamento.registrar_interacao(TipoInteracao.REUNIAO, "Visita", agora=AGORA)

    assert orcamento.interacoes == (primeira, segunda)


@pytest.mark.parametrize("conteudo", ["", "   "])
def test_interacao_sem_conteudo_e_rejeitada(conteudo: str) -> None:
    orcamento = novo_orcamento()

    with pytest.raises(FormatoInvalido) as erro:
        orcamento.registrar_interacao(TipoInteracao.MENSAGEM, conteudo, agora=AGORA)

    assert erro.value.campo == "conteudo"
    assert orcamento.interacoes == ()


@pytest.mark.parametrize("terminal", [E.FECHADO, E.PERDIDO])
def test_interacao_pode_ser_registrada_apos_encerramento(terminal: EstagioAtendimento) -> None:
    orcamento = orcamento_em(terminal)

    orcamento.registrar_interacao(TipoInteracao.MENSAGEM, "Pós-venda", agora=AGORA)

    assert len(orcamento.interacoes) == 1


def test_lista_de_interacoes_nao_pode_ser_alterada_por_fora() -> None:
    orcamento = novo_orcamento()

    assert isinstance(orcamento.interacoes, tuple)
