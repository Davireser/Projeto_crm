import { NextResponse, type NextRequest } from "next/server";

import { decidirAcesso } from "@/lib/sessao/acesso";
import { COOKIE_SESSAO, lerClaims } from "@/lib/sessao/token";

/** Redireciona antes de renderizar: sem sessão vai para o login; /usuarios só para admin. */
export function proxy(request: NextRequest) {
  const claims = lerClaims(request.cookies.get(COOKIE_SESSAO)?.value);
  const decisao = decidirAcesso(request.nextUrl.pathname, claims, Date.now() / 1000);
  if (decisao.tipo === "seguir") return NextResponse.next();

  const resposta = NextResponse.redirect(new URL(decisao.para, request.url));
  if (decisao.limparCookie) resposta.cookies.delete(COOKIE_SESSAO);
  return resposta;
}

export const config = {
  // Fora: rotas de API (o repasse trata a sessão) e arquivos estáticos.
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico|icon|manifest.webmanifest|robots.txt).*)"],
};
