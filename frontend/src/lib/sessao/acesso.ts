import { sessaoValida, type ClaimsSessao } from "./token";

export const PAGINA_INICIAL = "/painel";
const PAGINAS_PUBLICAS = ["/login"];
const SO_ADMINISTRADOR = ["/usuarios"];

export type Decisao =
  | { tipo: "seguir" }
  | { tipo: "redirecionar"; para: string; limparCookie?: true };

const comecaCom = (caminho: string, prefixos: string[]) =>
  prefixos.some((p) => caminho === p || caminho.startsWith(`${p}/`));

/**
 * Checagem otimista feita pelo `proxy.ts` antes de renderizar a página (RNF07).
 * Só olha o JWT do cookie; o backend continua recusando o que não for permitido.
 */
export function decidirAcesso(
  caminho: string,
  claims: ClaimsSessao | null,
  agoraEmSegundos: number,
): Decisao {
  const logado = sessaoValida(claims, agoraEmSegundos);

  if (caminho === "/") return { tipo: "redirecionar", para: logado ? PAGINA_INICIAL : "/login" };

  if (comecaCom(caminho, PAGINAS_PUBLICAS)) {
    return logado ? { tipo: "redirecionar", para: PAGINA_INICIAL } : { tipo: "seguir" };
  }

  if (!logado) {
    const para = `/login?de=${encodeURIComponent(caminho)}`;
    return claims ? { tipo: "redirecionar", para, limparCookie: true } : { tipo: "redirecionar", para };
  }

  if (comecaCom(caminho, SO_ADMINISTRADOR) && claims.perfil !== "ADMINISTRADOR") {
    return { tipo: "redirecionar", para: PAGINA_INICIAL };
  }
  return { tipo: "seguir" };
}

/** Só aceita caminhos internos (`/algo`), nunca outro site (`//x.com`, `https://...`). */
export function destinoSeguro(de: FormDataEntryValue | string | null | undefined): string {
  if (typeof de !== "string" || !de.startsWith("/") || de.startsWith("//") || de.includes("\\")) {
    return PAGINA_INICIAL;
  }
  return de;
}
