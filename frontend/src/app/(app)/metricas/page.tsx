import type { Metadata } from "next";

import { EmConstrucao } from "@/components/layout/em-construcao";

export const metadata: Metadata = { title: "Métricas" };

export default function Pagina() {
  return <EmConstrucao titulo="Métricas" parte="F6" descricao="Orçamentos em aberto, fechados, perdidos e taxa de fechamento." />;
}
