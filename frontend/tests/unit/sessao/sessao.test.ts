import { describe, expect, it, vi } from "vitest";

import { decidirAcesso, destinoSeguro } from "@/lib/sessao/acesso";
import { autenticar } from "@/lib/sessao/autenticar";
import { repassarParaApi } from "@/lib/sessao/repasse";
import { lerClaims, sessaoValida } from "@/lib/sessao/token";

const AGORA = 1_800_000_000;

function jwt(payload: object): string {
  const parte = (obj: object) => Buffer.from(JSON.stringify(obj)).toString("base64url");
  return `${parte({ alg: "HS256" })}.${parte(payload)}.assinatura`;
}

const ADMIN = jwt({ sub: "u1", perfil: "ADMINISTRADOR", exp: AGORA + 60 });
const COMUM = jwt({ sub: "u2", perfil: "USUARIO", exp: AGORA + 60 });
const VENCIDO = jwt({ sub: "u2", perfil: "USUARIO", exp: AGORA - 1 });

describe("token da sessão", () => {
  it("lê sub, perfil e exp do JWT", () => {
    expect(lerClaims(ADMIN)).toEqual({ sub: "u1", perfil: "ADMINISTRADOR", exp: AGORA + 60 });
  });

  it.each([undefined, "", "abc", "a.b.c", jwt({ sub: "u1" }), jwt({ sub: 1, perfil: "X", exp: 1 })])(
    "token malformado vira null: %j",
    (token) => {
      expect(lerClaims(token)).toBeNull();
    },
  );

  it("sessão vence no exp", () => {
    expect(sessaoValida(lerClaims(COMUM), AGORA)).toBe(true);
    expect(sessaoValida(lerClaims(VENCIDO), AGORA)).toBe(false);
    expect(sessaoValida(null, AGORA)).toBe(false);
  });
});

describe("decidirAcesso — checagem otimista do proxy.ts (RNF07)", () => {
  const decidir = (caminho: string, token?: string) => decidirAcesso(caminho, lerClaims(token), AGORA);

  it("sem sessão vai para o login guardando o destino", () => {
    expect(decidir("/painel")).toEqual({ tipo: "redirecionar", para: "/login?de=%2Fpainel" });
  });

  it("sessão vencida também limpa o cookie", () => {
    expect(decidir("/metricas", VENCIDO)).toEqual({
      tipo: "redirecionar",
      para: "/login?de=%2Fmetricas",
      limparCookie: true,
    });
  });

  it("login é público, mas quem já entrou vai para o painel", () => {
    expect(decidir("/login")).toEqual({ tipo: "seguir" });
    expect(decidir("/login", COMUM)).toEqual({ tipo: "redirecionar", para: "/painel" });
  });

  it("raiz vai para o painel", () => {
    expect(decidir("/", COMUM)).toEqual({ tipo: "redirecionar", para: "/painel" });
    expect(decidir("/")).toEqual({ tipo: "redirecionar", para: "/login" });
  });

  it("/usuarios só para administrador", () => {
    expect(decidir("/usuarios", COMUM)).toEqual({ tipo: "redirecionar", para: "/painel" });
    expect(decidir("/usuarios", ADMIN)).toEqual({ tipo: "seguir" });
  });

  it("demais rotas seguem com sessão válida", () => {
    expect(decidir("/clientes/abc", COMUM)).toEqual({ tipo: "seguir" });
  });
});

describe("destinoSeguro — evita redirecionar para outro site", () => {
  it.each([
    ["/metricas", "/metricas"],
    ["/clientes/1?x=2", "/clientes/1?x=2"],
    ["https://malicioso.com", "/painel"],
    ["//malicioso.com", "/painel"],
    ["/\\malicioso.com", "/painel"],
    [null, "/painel"],
    ["", "/painel"],
  ])("%j → %j", (de, esperado) => {
    expect(destinoSeguro(de)).toBe(esperado);
  });
});

function fetchQueResponde(status: number, corpo: unknown) {
  return vi.fn(async (_url: string | URL | Request, _init?: RequestInit) =>
    new Response(JSON.stringify(corpo), { status }),
  ) as unknown as typeof fetch & { mock: { calls: [string, RequestInit][] } };
}

describe("autenticar", () => {
  const TOKEN = {
    accessToken: ADMIN,
    tokenType: "bearer",
    expiraEm: "2027-01-15T08:00:00Z",
    usuario: { id: "u1", nome: "Davi", email: "davi@x.com", perfil: "ADMINISTRADOR", ativo: true },
  };

  it("valida o e-mail antes de chamar a API", async () => {
    const fetchFn = fetchQueResponde(200, TOKEN);

    expect(await autenticar("davi", "x", { base: "http://api", fetch: fetchFn })).toEqual({
      ok: false,
      erro: "E-mail inválido: 'davi'.",
    });
    expect(await autenticar("davi@x.com", "", { base: "http://api", fetch: fetchFn })).toEqual({
      ok: false,
      erro: "Informe a senha.",
    });
    expect(fetchFn).not.toHaveBeenCalled();
  });

  it("devolve o token e a validade", async () => {
    const fetchFn = fetchQueResponde(200, TOKEN);

    const resultado = await autenticar(" Davi@X.com ", "segredo", { base: "http://api/api/v1", fetch: fetchFn });

    expect(resultado).toEqual({ ok: true, token: ADMIN, expiraEm: new Date("2027-01-15T08:00:00Z") });
    const [url, init] = fetchFn.mock.calls[0]!;
    expect(url).toBe("http://api/api/v1/auth/login");
    expect(JSON.parse(String(init.body))).toEqual({ email: "davi@x.com", senha: "segredo" });
  });

  it("credenciais erradas viram mensagem amigável", async () => {
    const fetchFn = fetchQueResponde(401, { erro: "CredenciaisInvalidas", mensagem: "x", campo: null });

    expect(await autenticar("davi@x.com", "errada", { base: "http://api", fetch: fetchFn })).toEqual({
      ok: false,
      erro: "E-mail ou senha incorretos.",
    });
  });

  it("servidor fora do ar", async () => {
    const fetchFn = vi.fn(async () => {
      throw new TypeError("fetch failed");
    }) as unknown as typeof fetch;

    const resultado = await autenticar("davi@x.com", "x", { base: "http://api", fetch: fetchFn });

    expect(resultado).toEqual({ ok: false, erro: expect.stringMatching(/servidor/) });
  });

  it("outro erro da API mostra a mensagem dela", async () => {
    const fetchFn = fetchQueResponde(403, { erro: "AcessoNegado", mensagem: "Usuário desativado.", campo: null });

    expect(await autenticar("davi@x.com", "x", { base: "http://api", fetch: fetchFn })).toEqual({
      ok: false,
      erro: "Usuário desativado.",
    });
  });
});

describe("repassarParaApi — o navegador fala só com o Next", () => {
  it("repassa método, caminho, busca, corpo e o token do cookie", async () => {
    const fetchFn = fetchQueResponde(200, [{ id: "o1" }]);

    const resposta = await repassarParaApi({
      metodo: "PATCH",
      segmentos: ["orcamentos", "o1", "estagio"],
      busca: "?x=1",
      corpo: '{"estagio":"FECHADO"}',
      token: ADMIN,
      base: "http://api/api/v1",
      fetch: fetchFn,
    });

    expect(resposta.status).toBe(200);
    const [url, init] = fetchFn.mock.calls[0]!;
    expect(url).toBe("http://api/api/v1/orcamentos/o1/estagio?x=1");
    expect(init.method).toBe("PATCH");
    expect(init.body).toBe('{"estagio":"FECHADO"}');
    expect(new Headers(init.headers).get("authorization")).toBe(`Bearer ${ADMIN}`);
  });

  it("sem token responde 401 sem chamar a API", async () => {
    const fetchFn = fetchQueResponde(200, {});

    const resposta = await repassarParaApi({ metodo: "GET", segmentos: ["orcamentos"], busca: "", corpo: null, token: undefined, base: "http://api", fetch: fetchFn });

    expect(resposta.status).toBe(401);
    expect(await resposta.json()).toMatchObject({ erro: "NaoAutenticado" });
    expect(fetchFn).not.toHaveBeenCalled();
  });

  it("recusa caminho com '..'", async () => {
    const fetchFn = fetchQueResponde(200, {});

    const resposta = await repassarParaApi({ metodo: "GET", segmentos: ["..", "admin"], busca: "", corpo: null, token: ADMIN, base: "http://api", fetch: fetchFn });

    expect(resposta.status).toBe(400);
    expect(fetchFn).not.toHaveBeenCalled();
  });

  it("API fora do ar vira 503 no formato de erro padrão", async () => {
    const fetchFn = vi.fn(async () => {
      throw new TypeError("fetch failed");
    }) as unknown as typeof fetch;

    const resposta = await repassarParaApi({ metodo: "GET", segmentos: ["orcamentos"], busca: "", corpo: null, token: ADMIN, base: "http://api", fetch: fetchFn });

    expect(resposta.status).toBe(503);
    expect(await resposta.json()).toMatchObject({ erro: "ServicoIndisponivel" });
  });

  it("204 passa sem corpo", async () => {
    const fetchFn = vi.fn(async () => new Response(null, { status: 204 })) as unknown as typeof fetch;

    const resposta = await repassarParaApi({ metodo: "PATCH", segmentos: ["x"], busca: "", corpo: "{}", token: ADMIN, base: "http://api", fetch: fetchFn });

    expect(resposta.status).toBe(204);
  });
});
