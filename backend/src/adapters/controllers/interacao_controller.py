from uuid import UUID

from fastapi import APIRouter, status

from adapters.controllers.dependencias import Orcamentos, RelogioDaApp
from adapters.schemas.interacao_schema import InteracaoSaida, NovaInteracaoEntrada
from application.use_cases.registrar_interacao import RegistrarInteracaoUseCase

router = APIRouter(prefix="/orcamentos", tags=["interacoes"])


@router.post("/{orcamento_id}/interacoes", status_code=status.HTTP_201_CREATED)
def registrar_interacao(
    orcamento_id: UUID,
    entrada: NovaInteracaoEntrada,
    orcamentos: Orcamentos,
    relogio: RelogioDaApp,
) -> InteracaoSaida:
    """UC06: registra a interação pelo agregado Orcamento, com data/hora do sistema (RF04)."""
    use_case = RegistrarInteracaoUseCase(orcamentos, relogio)
    return InteracaoSaida.de(use_case.executar(orcamento_id, entrada.tipo, entrada.conteudo))
