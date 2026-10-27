from datetime import date
from decimal import Decimal
from typing import Self
from uuid import UUID

from adapters.schemas.base import Esquema, exemplo
from application.use_cases.consultar_metricas import MetricasFunil
from application.use_cases.consultar_orcamentos import CardOrcamento
from domain.entities.orcamento import Orcamento
from domain.value_objects.estagio_atendimento import TRANSICOES_PERMITIDAS, EstagioAtendimento


class MoverEstagioEntrada(Esquema):
    model_config = exemplo({"estagio": "EM_NEGOCIACAO"})

    estagio: EstagioAtendimento


class DefinirValorEntrada(Esquema):
    model_config = exemplo({"valor": "4200.00"})

    valor: Decimal


class OrcamentoSaida(Esquema):
    id: UUID
    cliente_id: UUID
    estagio: EstagioAtendimento
    valor: Decimal | None
    data_abertura: date
    data_fechamento: date | None

    @classmethod
    def de(cls, orcamento: Orcamento) -> Self:
        return cls(
            id=orcamento.id,
            cliente_id=orcamento.cliente_id,
            estagio=orcamento.estagio,
            valor=orcamento.valor.valor if orcamento.valor else None,
            data_abertura=orcamento.data_abertura,
            data_fechamento=orcamento.data_fechamento,
        )


class CardSaida(Esquema):
    """Card do Kanban — projeção enxuta, sem as interações (RNF01)."""

    id: UUID
    cliente_id: UUID
    cliente_nome: str
    estagio: EstagioAtendimento
    valor: Decimal | None
    data_abertura: date
    qtd_interacoes: int

    @classmethod
    def de(cls, card: CardOrcamento) -> Self:
        return cls(
            id=card.id,
            cliente_id=card.cliente_id,
            cliente_nome=card.cliente_nome,
            estagio=card.estagio,
            valor=card.valor,
            data_abertura=card.data_abertura,
            qtd_interacoes=card.qtd_interacoes,
        )


class TransicoesSaida(Esquema):
    """Mapa para o Kanban destacar as colunas válidas — derivado do mesmo enum do domínio."""

    transicoes: dict[EstagioAtendimento, list[EstagioAtendimento]]
    exigem_valor: list[EstagioAtendimento]

    @classmethod
    def do_dominio(cls) -> Self:
        return cls(
            transicoes={
                origem: [e for e in EstagioAtendimento if e in TRANSICOES_PERMITIDAS[origem]]
                for origem in EstagioAtendimento
            },
            exigem_valor=[e for e in EstagioAtendimento if e.exige_valor()],
        )


class MetricasSaida(Esquema):
    em_aberto: int
    fechados: int
    perdidos: int
    taxa_fechamento: Decimal | None

    @classmethod
    def de(cls, metricas: MetricasFunil) -> Self:
        return cls(
            em_aberto=metricas.em_aberto,
            fechados=metricas.fechados,
            perdidos=metricas.perdidos,
            taxa_fechamento=metricas.taxa_fechamento,
        )
