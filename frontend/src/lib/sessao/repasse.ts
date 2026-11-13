interface PedidoDeRepasse {
  metodo: string;
  segmentos: string[];
  /** Query string original, com o `?` (ou vazia). */
  busca: string;
  corpo: string | null;
  token: string | undefined;
  /** URL base da API, já com `/api/v1`. */
  base: string;
  fetch?: typeof fetch;
}

const erro = (status: number, codigo: string, mensagem: string) =>
  Response.json({ erro: codigo, mensagem, campo: null }, { status });

/**
 * Repassa uma chamada do navegador (`/api/...`) para o backend, colocando o JWT
 * que está no cookie httpOnly. Assim o token nunca fica exposto ao JavaScript
 * da página e o backend não precisa liberar CORS para o frontend.
 */
export async function repassarParaApi(pedido: PedidoDeRepasse): Promise<Response> {
  if (!pedido.token) return erro(401, "NaoAutenticado", "Sua sessão terminou. Entre de novo.");
  if (pedido.segmentos.some((s) => s === ".." || s === "." || s.includes("/"))) {
    return erro(400, "CaminhoInvalido", "Caminho inválido.");
  }

  const url = `${pedido.base.replace(/\/+$/, "")}/${pedido.segmentos.map(encodeURIComponent).join("/")}${pedido.busca}`;
  const headers = new Headers({ accept: "application/json", authorization: `Bearer ${pedido.token}` });
  if (pedido.corpo !== null) headers.set("content-type", "application/json");

  let resposta: Response;
  try {
    resposta = await (pedido.fetch ?? fetch)(url, {
      method: pedido.metodo,
      headers,
      body: pedido.corpo,
      cache: "no-store",
    });
  } catch {
    return erro(503, "ServicoIndisponivel", "Não foi possível falar com o servidor.");
  }

  const corpo = resposta.status === 204 ? null : await resposta.text();
  return new Response(corpo, {
    status: resposta.status,
    headers: { "content-type": resposta.headers.get("content-type") ?? "application/json" },
  });
}
