import type { Metadata } from "next";

import { EmConstrucao } from "@/components/layout/em-construcao";

export const metadata: Metadata = { title: "Usuários" };

export default function Pagina() {
  return <EmConstrucao titulo="Usuários" parte="F6" descricao="Listar, criar, editar e ativar ou desativar usuários (só administrador)." />;
}
