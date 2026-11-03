import { ErroRemoto } from "@/application/errors";

export interface OpcoesClienteHttp {
  fetch?: typeof fetch;
  /** Token JWT, quando a chamada sai do servidor (no navegador o proxy do Next coloca). */
  token?: () => string | undefined;
}

/** Wrapper de `fetch` que fala JSON e converte erros no `ErroRemoto` da aplicação. */
export class ClienteHttp {
  private readonly base: string;
  private readonly fetchFn: typeof fetch;
  private readonly token: () => string | undefined;

  constructor(base: string, opcoes: OpcoesClienteHttp = {}) {
    this.base = base.replace(/\/+$/, "");
    this.fetchFn = opcoes.fetch ?? ((...args) => fetch(...args));
    this.token = opcoes.token ?? (() => undefined);
  }

  get<T>(caminho: string): Promise<T> {
    return this.requisitar<T>("GET", caminho);
  }

  post<T>(caminho: string, corpo: unknown): Promise<T> {
    return this.requisitar<T>("POST", caminho, corpo);
  }

  patch<T>(caminho: string, corpo: unknown): Promise<T> {
    return this.requisitar<T>("PATCH", caminho, corpo);
  }

  private async requisitar<T>(metodo: string, caminho: string, corpo?: unknown): Promise<T> {
    const headers = new Headers({ accept: "application/json" });
    if (corpo !== undefined) headers.set("content-type", "application/json");
    const token = this.token();
    if (token) headers.set("authorization", `Bearer ${token}`);

    let resposta: Response;
    try {
      resposta = await this.fetchFn(`${this.base}${caminho}`, {
        method: metodo,
        headers,
        body: corpo === undefined ? undefined : JSON.stringify(corpo),
        cache: "no-store",
      });
    } catch {
      throw new ErroRemoto(0, "SemConexao", "Sem conexão com o servidor. Tente de novo.");
    }

    if (resposta.status === 204) return undefined as T;
    const dados: unknown = await resposta.json().catch(() => null);
    if (!resposta.ok) throw erroDaResposta(resposta.status, dados);
    return dados as T;
  }
}

function erroDaResposta(status: number, dados: unknown): ErroRemoto {
  if (typeof dados === "object" && dados !== null && "mensagem" in dados) {
    const { erro, mensagem, campo } = dados as { erro?: string; mensagem: string; campo?: string | null };
    return new ErroRemoto(status, erro ?? "Erro", mensagem, campo ?? null);
  }
  return new ErroRemoto(status, "Erro", "O servidor não conseguiu atender o pedido.");
}
