import { ErroRemoto } from "@/application/errors";
import { ErroDominio } from "@/domain/errors";
import { Email } from "@/domain/value-objects/email";
import { ClienteHttp } from "@/infra/http/cliente-http";
import type { TokenDto } from "@/infra/http/dtos";

export type ResultadoLogin =
  | { ok: true; token: string; expiraEm: Date }
  | { ok: false; erro: string };

interface Opcoes {
  /** URL base da API, já com `/api/v1`. */
  base: string;
  fetch?: typeof fetch;
}

/** Troca e-mail e senha pelo JWT do backend, com mensagens prontas para a tela. */
export async function autenticar(email: string, senha: string, opcoes: Opcoes): Promise<ResultadoLogin> {
  let endereco: string;
  try {
    endereco = Email.criar(email).endereco;
  } catch (erro) {
    if (erro instanceof ErroDominio) return { ok: false, erro: erro.mensagem };
    throw erro;
  }
  if (!senha) return { ok: false, erro: "Informe a senha." };

  try {
    const http = new ClienteHttp(opcoes.base, { fetch: opcoes.fetch });
    const resposta = await http.post<TokenDto>("/auth/login", { email: endereco, senha });
    return { ok: true, token: resposta.accessToken, expiraEm: new Date(resposta.expiraEm) };
  } catch (erro) {
    if (!(erro instanceof ErroRemoto)) throw erro;
    if (erro.sessaoExpirada) return { ok: false, erro: "E-mail ou senha incorretos." };
    if (erro.semConexao) {
      return { ok: false, erro: "Não foi possível falar com o servidor. Verifique se a API está no ar." };
    }
    return { ok: false, erro: erro.mensagem };
  }
}
