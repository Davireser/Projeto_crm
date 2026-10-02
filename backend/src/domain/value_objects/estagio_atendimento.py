from collections.abc import Mapping
from enum import StrEnum
from typing import Final


class EstagioAtendimento(StrEnum):
    """Os cinco estágios do funil. Conjunto fechado — ver 10-diagrama-estados.md."""

    NOVO_CONTATO = "NOVO_CONTATO"
    EM_NEGOCIACAO = "EM_NEGOCIACAO"
    ORCAMENTO_ENVIADO = "ORCAMENTO_ENVIADO"
    FECHADO = "FECHADO"
    PERDIDO = "PERDIDO"

    def pode_mover_para(self, destino: "EstagioAtendimento") -> bool:
        return destino in TRANSICOES_PERMITIDAS[self]

    def eh_terminal(self) -> bool:
        return not TRANSICOES_PERMITIDAS[self]

    def exige_valor(self) -> bool:
        """Guarda [valorDefinido] (RN02): só se entra neste estágio com valor."""
        return self in _ESTAGIOS_QUE_EXIGEM_VALOR


# RN01 — fonte única de verdade, também exposta ao frontend via GET /orcamentos/transicoes.
TRANSICOES_PERMITIDAS: Final[Mapping[EstagioAtendimento, frozenset[EstagioAtendimento]]] = {
    EstagioAtendimento.NOVO_CONTATO: frozenset(
        {EstagioAtendimento.EM_NEGOCIACAO, EstagioAtendimento.PERDIDO}
    ),
    EstagioAtendimento.EM_NEGOCIACAO: frozenset(
        {EstagioAtendimento.ORCAMENTO_ENVIADO, EstagioAtendimento.PERDIDO}
    ),
    EstagioAtendimento.ORCAMENTO_ENVIADO: frozenset(
        {EstagioAtendimento.FECHADO, EstagioAtendimento.PERDIDO}
    ),
    EstagioAtendimento.FECHADO: frozenset(),
    EstagioAtendimento.PERDIDO: frozenset(),
}

_ESTAGIOS_QUE_EXIGEM_VALOR: Final = frozenset(
    {EstagioAtendimento.ORCAMENTO_ENVIADO, EstagioAtendimento.FECHADO}
)
