import { onlineManager, QueryClient, QueryClientProvider, useMutation } from "@tanstack/react-query";
import { act, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { ErroRemoto } from "@/application/errors";
import { StatusConexao } from "@/components/kanban/status-conexao";
import { ClienteHttp } from "@/infra/http/cliente-http";
import { criarApiHttp, useApi } from "@/lib/api/api-navegador";
import { criarQueryClient } from "@/lib/query/provedor-query";

import { MAPA_DA_API } from "../unit/domain/fixtures";

afterEach(() => {
  act(() => onlineManager.setOnline(true));
});

describe("StatusConexao (offline first)", () => {
  function Pendente() {
    const mutacao = useMutation({ mutationFn: () => new Promise(() => {}) });
    return <button onClick={() => mutacao.mutate()}>alterar</button>;
  }

  it("online e sem pendências não mostra nada", () => {
    render(
      <QueryClientProvider client={new QueryClient()}>
        <StatusConexao />
      </QueryClientProvider>,
    );

    expect(screen.queryByRole("status")).not.toBeInTheDocument();
  });

  it("offline mostra quantas alterações aguardam envio", async () => {
    render(
      <QueryClientProvider client={new QueryClient()}>
        <StatusConexao />
        <Pendente />
      </QueryClientProvider>,
    );

    act(() => onlineManager.setOnline(false));
    expect(screen.getByRole("status")).toHaveTextContent("Offline");

    act(() => screen.getByRole("button", { name: "alterar" }).click());
    expect(await screen.findByText(/1 alteração aguardando/)).toBeInTheDocument();
  });

  it("online com alteração em andamento mostra sincronizando", async () => {
    render(
      <QueryClientProvider client={new QueryClient()}>
        <StatusConexao />
        <Pendente />
      </QueryClientProvider>,
    );

    act(() => screen.getByRole("button", { name: "alterar" }).click());

    expect(await screen.findByRole("status")).toHaveTextContent("Sincronizando");
  });
});

describe("criarQueryClient — nova tentativa", () => {
  const tentar = (vezes: number, erro: unknown) => {
    const retry = criarQueryClient(() => {}).getDefaultOptions().queries?.retry;
    if (typeof retry !== "function") throw new Error("retry deveria ser função");
    return retry(vezes, erro as Error);
  };

  it("não insiste em erro do cliente (4xx), insiste em falha de rede ou 5xx", () => {
    expect(tentar(0, new ErroRemoto(404, "X", "Não achou"))).toBe(false);
    expect(tentar(0, new ErroRemoto(0, "SemConexao", "Sem rede"))).toBe(true);
    expect(tentar(1, new ErroRemoto(503, "X", "Fora do ar"))).toBe(true);
    expect(tentar(2, new ErroRemoto(503, "X", "Fora do ar"))).toBe(false);
  });
});

describe("API do navegador", () => {
  it("busca o painel pelo proxy /api do Next", async () => {
    const fetchFn = vi.fn(async (url: string | URL | Request) =>
      Response.json(String(url).endsWith("/transicoes") ? MAPA_DA_API : []),
    ) as unknown as typeof fetch;

    const painel = await criarApiHttp(new ClienteHttp("/api", { fetch: fetchFn })).buscarPainel();

    expect(painel).toEqual({ cards: [], mapa: MAPA_DA_API });
    expect(vi.mocked(fetchFn).mock.calls.map(([url]) => String(url)).sort()).toEqual([
      "/api/orcamentos",
      "/api/orcamentos/transicoes",
    ]);
  });

  it("useApi fora do provedor avisa o erro de montagem", () => {
    function SemProvedor() {
      useApi();
      return null;
    }
    vi.spyOn(console, "error").mockImplementation(() => {});

    expect(() => render(<SemProvedor />)).toThrow(/ProvedorApi/);
  });
});

describe("criarQueryClient — sessão expirada", () => {
  it("leva ao login quando a API responde 401, em consultas e alterações", async () => {
    const aoExpirar = vi.fn();
    const client = criarQueryClient(aoExpirar);
    const expirou = new ErroRemoto(401, "NaoAutenticado", "Sessão expirada");

    await client.fetchQuery({ queryKey: ["x"], queryFn: () => Promise.reject(expirou), retry: false }).catch(() => {});
    await client
      .getMutationCache()
      .build(client, { mutationFn: () => Promise.reject(new ErroRemoto(422, "X", "Inválido")) })
      .execute(undefined)
      .catch(() => {});

    expect(aoExpirar).toHaveBeenCalledTimes(1);
  });
});
