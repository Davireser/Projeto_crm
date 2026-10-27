from uuid import UUID

from application.relogio import Relogio
from application.use_cases.comum import obter_orcamento
from domain.entities.orcamento import Orcamento
from domain.repositories.orcamento_repository import OrcamentoRepository
from domain.value_objects.estagio_atendimento import EstagioAtendimento


class MoverEstagioUseCase:
    """UC03 (inclui UC04): carrega, delega a decisão ao Orcamento e salva se ele aceitar.

    O caso de uso não decide nada sobre a transição. Se o domínio lança
    `TransicaoInvalida`, a exceção sobe antes de `salvar()` (RNF04).
    """

    def __init__(self, orcamentos: OrcamentoRepository, relogio: Relogio) -> None:
        self._orcamentos = orcamentos
        self._relogio = relogio

    def executar(self, orcamento_id: UUID, novo_estagio: EstagioAtendimento) -> Orcamento:
        orcamento = obter_orcamento(self._orcamentos, orcamento_id)
        orcamento.mover_estagio(novo_estagio, hoje=self._relogio().date())
        self._orcamentos.salvar(orcamento)
        return orcamento
