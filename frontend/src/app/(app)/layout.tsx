import Link from "next/link";
import { Suspense } from "react";

import { LinkNav } from "@/components/layout/link-nav";
import { MenuUsuario } from "@/components/layout/menu-usuario";
import { Skeleton } from "@/components/ui/skeleton";

/**
 * Layout da área logada. O cabeçalho é estático (vai no shell pré-renderizado);
 * só o menu do usuário, que lê a sessão, espera a requisição dentro do Suspense.
 */
export default function LayoutApp({ children }: LayoutProps<"/">) {
  return (
    <div className="flex min-h-full flex-col">
      <header className="sticky top-0 z-10 border-b bg-background/95 backdrop-blur">
        <div className="mx-auto flex h-14 max-w-7xl items-center gap-4 px-4">
          <Link href="/painel" className="font-semibold tracking-tight">
            CRM <span className="text-muted-foreground">Orçamentos</span>
          </Link>
          <nav aria-label="Principal" className="flex flex-1 items-center gap-1 overflow-x-auto">
            <LinkNav href="/painel">Painel</LinkNav>
            <LinkNav href="/contatos/novo">Novo contato</LinkNav>
            <LinkNav href="/metricas">Métricas</LinkNav>
          </nav>
          <Suspense fallback={<Skeleton className="h-8 w-32" />}>
            <MenuUsuario />
          </Suspense>
        </div>
      </header>
      <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-6">{children}</main>
    </div>
  );
}
