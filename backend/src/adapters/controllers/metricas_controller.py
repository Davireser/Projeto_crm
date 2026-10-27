from fastapi import APIRouter

from adapters.controllers.dependencias import Orcamentos
from adapters.schemas.orcamento_schema import MetricasSaida
from application.use_cases.consultar_metricas import ConsultarMetricasUseCase

router = APIRouter(prefix="/metricas", tags=["metricas"])


@router.get("/funil")
def consultar_metricas(orcamentos: Orcamentos) -> MetricasSaida:
    """UC08: orçamentos em aberto e taxa de fechamento (RF06, RN07)."""
    return MetricasSaida.de(ConsultarMetricasUseCase(orcamentos).executar())
