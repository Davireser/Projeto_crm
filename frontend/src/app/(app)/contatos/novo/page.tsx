import type { Metadata } from "next";

import { EmConstrucao } from "@/components/layout/em-construcao";

export const metadata: Metadata = { title: "Novo contato" };

export default function Pagina() {
  return <EmConstrucao titulo="Novo contato" parte="F5" descricao="Cadastro do cliente com o primeiro orçamento, validando telefone e e-mail." />;
}
