"use client";

import { useQuery } from "@tanstack/react-query";

import { ConsultarMetricas } from "@/application/use-cases/consultar-metricas";
import { MetricasFunil, type DadosMetricasFunil } from "@/domain/entities/metricas-funil";
import { useApi } from "@/lib/api/api-navegador";

import { CHAVE_METRICAS } from "./use-painel";

/**
 * Indicadores do funil (RF06). O cache guarda os dados simples (o persister
 * serializa em JSON) e o `select` devolve a entidade com `taxaFormatada()`.
 */
export function useMetricas(inicial?: DadosMetricasFunil) {
  const api = useApi();
  return useQuery<DadosMetricasFunil, Error, MetricasFunil>({
    queryKey: CHAVE_METRICAS,
    queryFn: () => new ConsultarMetricas(api.metricas).executar(),
    initialData: inicial,
    select: (dados) => new MetricasFunil(dados),
  });
}
