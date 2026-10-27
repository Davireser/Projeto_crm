from uuid import UUID

from application.relogio import Relogio
from application.use_cases.comum import obter_orcamento
from domain.entities.interacao import Interacao
from domain.repositories.orcamento_repository import OrcamentoRepository
from domain.value_objects.tipo_interacao import TipoInteracao


class RegistrarInteracaoUseCase:
    """UC06: registra a interação através do agregado Orcamento, com data/hora do sistema (RF04)."""

    def __init__(self, orcamentos: OrcamentoRepository, relogio: Relogio) -> None:
        self._orcamentos = orcamentos
        self._relogio = relogio

    def executar(self, orcamento_id: UUID, tipo: TipoInteracao, conteudo: str) -> Interacao:
        orcamento = obter_orcamento(self._orcamentos, orcamento_id)
        interacao = orcamento.registrar_interacao(tipo, conteudo, agora=self._relogio())
        self._orcamentos.salvar(orcamento)
        return interacao
