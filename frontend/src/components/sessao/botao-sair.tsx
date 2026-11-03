"use client";

import { useQueryClient } from "@tanstack/react-query";
import { LogOut } from "lucide-react";
import { useTransition } from "react";

import { DropdownMenuItem } from "@/components/ui/dropdown-menu";
import { CHAVE_DO_CACHE } from "@/lib/query/provedor-query";

/** Sai da conta e apaga o cache offline, para o próximo usuário não ver os dados. */
export function BotaoSair({ sair }: { sair: () => Promise<void> }) {
  const queryClient = useQueryClient();
  const [saindo, iniciar] = useTransition();

  return (
    <DropdownMenuItem
      disabled={saindo}
      onSelect={() =>
        iniciar(async () => {
          queryClient.clear();
          window.localStorage.removeItem(CHAVE_DO_CACHE);
          await sair();
        })
      }
    >
      <LogOut aria-hidden />
      {saindo ? "Saindo…" : "Sair"}
    </DropdownMenuItem>
  );
}
