import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { Suspense } from "react";

import { ErroRemoto } from "@/application/errors";
import { EsqueletoMetricas, PainelMetricas } from "@/components/metricas/painel-metricas";
import type { DadosMetricasFunil } from "@/domain/entities/metricas-funil";
import { MetricasGatewayHttp } from "@/infra/http/gateways-http";
import { apiDoServidor } from "@/lib/sessao/servidor";

export const metadata: Metadata = {
  title: "Métricas",
  description: "Orçamentos em aberto, fechados, perdidos e a taxa de fechamento do funil.",
};

export default function Pagina() {
  return (
    <div className="grid gap-6">
      <header className="grid gap-1">
        <h1 className="text-2xl font-semibold tracking-tight">Métricas</h1>
        <p className="text-sm text-muted-foreground">Situação atual do funil de atendimento.</p>
      </header>
      <Suspense fallback={<EsqueletoMetricas />}>
        <MetricasComDados />
      </Suspense>
    </div>
  );
}

/** Primeira pintura com os números do servidor; depois o TanStack Query atualiza e guarda offline. */
async function MetricasComDados() {
  return <PainelMetricas inicial={await buscarMetricas()} />;
}

async function buscarMetricas(): Promise<DadosMetricasFunil | undefined> {
  try {
    // Só dados simples atravessam do servidor para o Client Component.
    return { ...(await new MetricasGatewayHttp(await apiDoServidor()).obter()) };
  } catch (erro) {
    if (erro instanceof ErroRemoto && erro.sessaoExpirada) redirect("/login?de=/metricas");
    return undefined;
  }
}
