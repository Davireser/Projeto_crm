import { cookies } from "next/headers";
import type { NextRequest } from "next/server";

import { URL_API } from "@/lib/config";
import { repassarParaApi } from "@/lib/sessao/repasse";
import { COOKIE_SESSAO } from "@/lib/sessao/token";

type Contexto = RouteContext<"/api/[...caminho]">;

async function repassar(request: NextRequest, contexto: Contexto): Promise<Response> {
  const { caminho } = await contexto.params;
  const loja = await cookies();
  const resposta = await repassarParaApi({
    metodo: request.method,
    segmentos: caminho,
    busca: request.nextUrl.search,
    corpo: request.method === "GET" ? null : await request.text(),
    token: loja.get(COOKIE_SESSAO)?.value,
    base: URL_API,
  });
  // Token recusado pelo backend: a sessão acabou, então o cookie sai também.
  if (resposta.status === 401) loja.delete(COOKIE_SESSAO);
  return resposta;
}

export const GET = repassar;
export const POST = repassar;
export const PATCH = repassar;
