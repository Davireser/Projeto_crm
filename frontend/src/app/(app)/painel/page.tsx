import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { Suspense } from "react";

import { ErroRemoto } from "@/application/errors";
import { EsqueletoKanban } from "@/components/kanban/esqueleto-kanban";
import { Kanban } from "@/components/kanban/kanban";
import type { MapaDeTransicoes } from "@/domain/funil/funil";
import type { CardDto } from "@/infra/http/dtos";
import type { PainelDto } from "@/lib/api/api-navegador";
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
    const http = await apiDoServidor();
    const [cards, mapa] = await Promise.all([
      http.get<CardDto[]>("/orcamentos"),
      http.get<MapaDeTransicoes>("/orcamentos/transicoes"),
    ]);
    return { cards, mapa };
  } catch (erro) {
    if (erro instanceof ErroRemoto && erro.sessaoExpirada) redirect("/login?de=/painel");
    // API fora do ar: o navegador tenta de novo e, se houver, mostra o cache offline.
    return undefined;
  }
}
