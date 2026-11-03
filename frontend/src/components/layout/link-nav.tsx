"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

/** Link do menu que se destaca quando a página atual pertence à seção. */
export function LinkNav({ href, children }: { href: string; children: ReactNode }) {
  const caminho = usePathname();
  const ativo = caminho === href || caminho.startsWith(`${href}/`);

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
