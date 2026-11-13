"use client";

import { createContext, use, useState, type ReactNode } from "react";

import type {
  ClienteGateway,
  MetricasGateway,
  OrcamentoGateway,
  UsuarioGateway,
} from "@/application/ports";
import { ClienteHttp } from "@/infra/http/cliente-http";
import type { PainelDto } from "@/infra/http/dtos";
import {
  buscarPainelDto,
  ClienteGatewayHttp,
  MetricasGatewayHttp,
  OrcamentoGatewayHttp,
  UsuarioGatewayHttp,
} from "@/infra/http/gateways-http";

export type { PainelDto };

/** O que os componentes do navegador usam para falar com o backend (via `/api` do Next). */
export interface ApiDoNavegador {
  buscarPainel(): Promise<PainelDto>;
  orcamentos: OrcamentoGateway;
  clientes: ClienteGateway;
  metricas: MetricasGateway;
  usuarios: UsuarioGateway;
}

export function criarApiHttp(http = new ClienteHttp("/api")): ApiDoNavegador {
  return {
    buscarPainel: () => buscarPainelDto(http),
    orcamentos: new OrcamentoGatewayHttp(http),
    clientes: new ClienteGatewayHttp(http),
    metricas: new MetricasGatewayHttp(http),
    usuarios: new UsuarioGatewayHttp(http),
  };
}

const ContextoApi = createContext<ApiDoNavegador | null>(null);

/** Injeção de dependência da interface: em produção HTTP, nos testes gateways em memória. */
export function ProvedorApi({ api, children }: { api?: ApiDoNavegador; children: ReactNode }) {
  const [valor] = useState(() => api ?? criarApiHttp());
  return <ContextoApi value={valor}>{children}</ContextoApi>;
}

export function useApi(): ApiDoNavegador {
  const api = use(ContextoApi);
  if (!api) throw new Error("useApi precisa estar dentro de <ProvedorApi>.");
  return api;
}
