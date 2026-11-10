"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Suspense, type ReactNode } from "react";

import { cn } from "@/lib/utils";

interface Props {
  href: string;
  children: ReactNode;
}

/**
 * Link do menu que se destaca quando a página atual pertence à seção.
 * Em rotas como `/clientes/[id]` o caminho só existe na requisição; o Suspense
 * deixa o menu ser pré-renderizado sem destaque e acende o link ao carregar.
 */
export function LinkNav(props: Props) {
  return (
    <Suspense fallback={<LinkDoMenu {...props} ativo={false} />}>
      <LinkComDestaque {...props} />
    </Suspense>
  );
}

function LinkComDestaque(props: Props) {
  const caminho = usePathname();
  return <LinkDoMenu {...props} ativo={caminho === props.href || caminho.startsWith(`${props.href}/`)} />;
}

function LinkDoMenu({ href, children, ativo }: Props & { ativo: boolean }) {
  return (
    <Link
      href={href}
      aria-current={ativo ? "page" : undefined}
      className={cn(
        "rounded-md px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground",
        ativo && "bg-accent text-accent-foreground",
      )}
    >
      {children}
    </Link>
  );
}
