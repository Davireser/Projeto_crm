import { PERFIS, type Perfil } from "@/domain/entities/usuario";

/** Cookie httpOnly que guarda o JWT emitido pelo backend. */
export const COOKIE_SESSAO = "crm_sessao";

export interface ClaimsSessao {
  sub: string;
  perfil: Perfil;
  /** Expiração em segundos desde 1970 (padrão JWT). */
  exp: number;
}

/**
 * Lê o conteúdo do JWT **sem verificar a assinatura**. Serve só para checagens
 * otimistas (redirecionar no `proxy.ts`); quem valida de verdade é o backend.
 */
export function lerClaims(token: string | undefined): ClaimsSessao | null {
  const conteudo = token?.split(".")[1];
  if (!conteudo) return null;
  try {
    const dados: unknown = JSON.parse(decodificarBase64Url(conteudo));
    if (typeof dados !== "object" || dados === null) return null;
    const { sub, perfil, exp } = dados as Record<string, unknown>;
    if (typeof sub !== "string" || typeof exp !== "number") return null;
    if (!(PERFIS as readonly unknown[]).includes(perfil)) return null;
    return { sub, perfil: perfil as Perfil, exp };
  } catch {
    return null;
  }
}

export function sessaoValida(claims: ClaimsSessao | null, agoraEmSegundos: number): claims is ClaimsSessao {
  return claims !== null && claims.exp > agoraEmSegundos;
}

function decodificarBase64Url(texto: string): string {
  const base64 = texto.replace(/-/g, "+").replace(/_/g, "/");
  const binario = atob(base64.padEnd(Math.ceil(base64.length / 4) * 4, "="));
  return new TextDecoder().decode(Uint8Array.from(binario, (c) => c.charCodeAt(0)));
}
