import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { Suspense } from "react";

import { ErroRemoto } from "@/application/errors";
import { EsqueletoKanban } from "@/components/kanban/esqueleto-kanban";
import { Kanban } from "@/components/kanban/kanban";
import type { PainelDto } from "@/infra/http/dtos";
import { buscarPainelDto } from "@/infra/http/gateways-http";
import { apiDoServidor } from "@/lib/sessao/servidor";

export const metadata: Metadata = {
  title: "Painel",
  description: "Kanban do funil de atendimento: novo contato, em negociação, orçamento enviado, fechado e perdido.",
};

export default function Pagina() {
  return (
    <Suspense fallback={<EsqueletoKanban />}>
      <PainelComDados />
    </Suspense>
  );
}

/**
 * Renderiza no servidor com os dados já buscados (primeira pintura sem spinner);
 * daí em diante o TanStack Query assume no navegador, com cache offline.
 */
async function PainelComDados() {
  return <Kanban inicial={await buscarPainel()} />;
}

async function buscarPainel(): Promise<PainelDto | undefined> {
  try {
    return await buscarPainelDto(await apiDoServidor());
  } catch (erro) {
    if (erro instanceof ErroRemoto && erro.sessaoExpirada) redirect("/login?de=/painel");
    // API fora do ar: o navegador tenta de novo e, se houver, mostra o cache offline.
    return undefined;
  }
}
