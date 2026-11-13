import "server-only";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { ErroRemoto } from "@/application/errors";
import type { Usuario } from "@/domain/entities/usuario";
import { ClienteHttp } from "@/infra/http/cliente-http";
import type { UsuarioDto } from "@/infra/http/dtos";
import { paraUsuario } from "@/infra/http/mapeadores";
import { EM_PRODUCAO, URL_API } from "@/lib/config";

import { COOKIE_SESSAO } from "./token";

/** Camada de acesso a dados da sessão: o único lugar que lê e grava o cookie. */

export async function lerToken(): Promise<string | undefined> {
  return (await cookies()).get(COOKIE_SESSAO)?.value;
}

export async function gravarSessao(token: string, expiraEm: Date): Promise<void> {
  (await cookies()).set(COOKIE_SESSAO, token, {
    httpOnly: true,
    sameSite: "lax",
    secure: EM_PRODUCAO,
    path: "/",
    expires: expiraEm,
  });
}

export async function apagarSessao(): Promise<void> {
  (await cookies()).delete(COOKIE_SESSAO);
}

/** Cliente HTTP para Server Components: fala direto com o backend, com o token. */
export async function apiDoServidor(): Promise<ClienteHttp> {
  const token = await lerToken();
  return new ClienteHttp(URL_API, { token: () => token });
}

/** Quem está logado, confirmado pelo backend (`GET /auth/eu`). Sem sessão, vai para o login. */
export async function usuarioAtual(): Promise<Usuario> {
  try {
    const http = await apiDoServidor();
    return paraUsuario(await http.get<UsuarioDto>("/auth/eu"));
  } catch (erro) {
    if (erro instanceof ErroRemoto && erro.sessaoExpirada) redirect("/login");
    throw erro;
  }
}
