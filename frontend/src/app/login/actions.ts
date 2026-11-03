"use server";

import { redirect } from "next/navigation";

import { URL_API } from "@/lib/config";
import { destinoSeguro } from "@/lib/sessao/acesso";
import { autenticar } from "@/lib/sessao/autenticar";
import type { EstadoLogin } from "@/lib/sessao/estado-login";
import { apagarSessao, gravarSessao } from "@/lib/sessao/servidor";

/** Server Action do login: o JWT vai direto para um cookie httpOnly, nunca para o navegador. */
export async function entrar(_anterior: EstadoLogin, form: FormData): Promise<EstadoLogin> {
  const email = String(form.get("email") ?? "");
  const resultado = await autenticar(email, String(form.get("senha") ?? ""), { base: URL_API });
  if (!resultado.ok) return { erro: resultado.erro, email };

  await gravarSessao(resultado.token, resultado.expiraEm);
  redirect(destinoSeguro(form.get("de")));
}

export async function sair(): Promise<void> {
  await apagarSessao();
  redirect("/login");
}
