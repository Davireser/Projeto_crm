"use client";

import { createSyncStoragePersister } from "@tanstack/query-sync-storage-persister";
import { MutationCache, QueryCache, QueryClient } from "@tanstack/react-query";
import { PersistQueryClientProvider } from "@tanstack/react-query-persist-client";
import { useRouter } from "next/navigation";
import { useState, type ReactNode } from "react";

import { ErroRemoto } from "@/application/errors";

export const CHAVE_DO_CACHE = "crm-cache";
const UM_DIA = 24 * 60 * 60 * 1000;
// Mudou o formato do que fica no cache? Troque a versão: o cache antigo é descartado.
const VERSAO_DO_CACHE = "2";

/** Exportado para os testes conferirem as regras de nova tentativa. */
export function criarQueryClient(aoExpirarSessao: () => void): QueryClient {
  const seSessaoExpirou = (erro: unknown) => {
    if (erro instanceof ErroRemoto && erro.sessaoExpirada) aoExpirarSessao();
  };
  return new QueryClient({
    queryCache: new QueryCache({ onError: seSessaoExpirou }),
    mutationCache: new MutationCache({ onError: seSessaoExpirou }),
    defaultOptions: {
      queries: {
        // Offline first: usa o cache persistido e busca de novo quando a rede volta.
        networkMode: "offlineFirst",
        staleTime: 30_000,
        gcTime: UM_DIA,
        retry: (tentativas, erro) =>
          !(erro instanceof ErroRemoto && erro.status >= 400 && erro.status < 500) && tentativas < 2,
      },
      // Sem rede, a alteração fica pausada (já aplicada na tela) e é enviada quando a conexão volta.
      mutations: { networkMode: "online" },
    },
  });
}

// No servidor não há `window`: sem storage, o persister do TanStack não faz nada.
const persistidor = createSyncStoragePersister({
  storage: typeof window === "undefined" ? undefined : window.localStorage,
  key: CHAVE_DO_CACHE,
});

export function ProvedorQuery({ children }: { children: ReactNode }) {
  const router = useRouter();
  // 401 em qualquer chamada: a rota /api já apagou o cookie; volta ao login lembrando a página.
  const [queryClient] = useState(() =>
    criarQueryClient(() => router.replace(`/login?de=${encodeURIComponent(window.location.pathname)}`)),
  );

  return (
    <PersistQueryClientProvider client={queryClient} persistOptions={{ persister: persistidor, maxAge: UM_DIA, buster: VERSAO_DO_CACHE }}>
      {children}
    </PersistQueryClientProvider>
  );
}
