from typing import Self
from uuid import UUID

from adapters.schemas.base import Esquema, InstanteUTC, exemplo
from application.use_cases.consultar_historico_cliente import ItemHistorico
from domain.entities.interacao import Interacao
from domain.value_objects.tipo_interacao import TipoInteracao


class NovaInteracaoEntrada(Esquema):
    model_config = exemplo({"tipo": "LIGACAO", "conteudo": "Pediu orçamento de 500 caixas."})

    tipo: TipoInteracao
    conteudo: str


class InteracaoSaida(Esquema):
    id: UUID
    tipo: TipoInteracao
    conteudo: str
    data_hora: InstanteUTC

    @classmethod
    def de(cls, interacao: Interacao) -> Self:
        return cls(
            id=interacao.id,
            tipo=interacao.tipo,
            conteudo=interacao.conteudo,
            data_hora=interacao.data_hora,
        )


class ItemHistoricoSaida(InteracaoSaida):
    """Interação na linha do tempo do cliente, com o orçamento de origem (RN08)."""

    orcamento_id: UUID

    @classmethod
    def do_item(cls, item: ItemHistorico) -> Self:
        interacao = item.interacao
        return cls(
            id=interacao.id,
            orcamento_id=item.orcamento_id,
            tipo=interacao.tipo,
            conteudo=interacao.conteudo,
            data_hora=interacao.data_hora,
        )
