import type { Metadata } from "next";
import { Suspense } from "react";

import { Skeleton } from "@/components/ui/skeleton";
import { GestaoUsuarios } from "@/components/usuarios/gestao-usuarios";
import { UsuarioGatewayHttp } from "@/infra/http/gateways-http";
import { apiDoServidor, usuarioAtual } from "@/lib/sessao/servidor";

export const metadata: Metadata = {
  title: "Usuários",
  description: "Cadastro de quem opera o CRM: criar, editar, ativar e desativar usuários.",
};

export default function Pagina() {
  return (
    <Suspense fallback={<Skeleton className="h-64" />}>
      <UsuariosComDados />
    </Suspense>
  );
}

/** A checagem de perfil é repetida aqui e no backend (RNF07); o menu só esconde o link. */
async function UsuariosComDados() {
  const eu = await usuarioAtual();
  if (!eu.podeGerenciarUsuarios()) return <AcessoRestrito />;

  const usuarios = await new UsuarioGatewayHttp(await apiDoServidor()).listar();
  // Só dados simples atravessam do servidor para o Client Component.
  return <GestaoUsuarios solicitante={{ ...eu }} inicial={usuarios.map((u) => ({ ...u }))} />;
}

function AcessoRestrito() {
  return (
    <div className="mx-auto grid max-w-md justify-items-center gap-2 py-16 text-center">
      <h1 className="text-xl font-semibold">Acesso restrito</h1>
      <p className="text-sm text-muted-foreground">Só administradores gerenciam usuários.</p>
    </div>
  );
}
