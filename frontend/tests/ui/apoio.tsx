import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import type { ReactElement } from "react";
import { Toaster } from "sonner";

import { paraCardDto } from "@/infra/http/mapeadores";
import { CrmEmMemoria, UsuariosEmMemoria } from "@/infra/memoria/crm-em-memoria";
import { ProvedorApi, type ApiDoNavegador } from "@/lib/api/api-navegador";

import { MAPA_DA_API } from "../unit/domain/fixtures";

/** API do navegador montada sobre os gateways em memória (sem rede). */
export function apiDeMemoria(crm: CrmEmMemoria): ApiDoNavegador {
  return {
    buscarPainel: async () => ({
      cards: (await crm.orcamentos.listarCards()).map(paraCardDto),
      mapa: await crm.orcamentos.obterTransicoes(),
    }),
    orcamentos: crm.orcamentos,
    clientes: crm.clientes,
    metricas: crm.metricas,
    usuarios: new UsuariosEmMemoria(),
  };
}

export function novoCrm(): CrmEmMemoria {
  return new CrmEmMemoria(MAPA_DA_API, () => new Date("2026-09-15T15:00:00Z"));
}

export function renderComApi(ui: ReactElement, api: ApiDoNavegador) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return {
    queryClient,
    ...render(
      <QueryClientProvider client={queryClient}>
        <ProvedorApi api={api}>{ui}</ProvedorApi>
        <Toaster />
      </QueryClientProvider>,
    ),
  };
}
