"use client";

import { onlineManager, useMutationState } from "@tanstack/react-query";
import { CloudOff, RefreshCw } from "lucide-react";
import { useSyncExternalStore } from "react";

import { Badge } from "@/components/ui/badge";

const assinar = (aviso: () => void) => onlineManager.subscribe(aviso);
const estaOnline = () => onlineManager.isOnline();

/** Avisa quando a página está offline e quantas alterações esperam para ser enviadas. */
export function StatusConexao() {
  const online = useSyncExternalStore(assinar, estaOnline, () => true);
  const pendentes = useMutationState({ filters: { status: "pending" } }).length;

  if (!online) {
    return (
      <Badge variant="outline" role="status" className="gap-1 border-amber-500 text-amber-700 dark:text-amber-400">
        <CloudOff className="size-3" aria-hidden />
        Offline
        {pendentes > 0 && ` · ${pendentes} ${pendentes === 1 ? "alteração aguardando" : "alterações aguardando"}`}
      </Badge>
    );
  }
  if (pendentes > 0) {
    return (
      <Badge variant="outline" role="status" className="gap-1">
        <RefreshCw className="size-3 animate-spin" aria-hidden />
        Sincronizando…
      </Badge>
    );
  }
  return null;
}
