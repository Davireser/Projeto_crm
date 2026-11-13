import { describe, expect, it, vi } from "vitest";

import { ErroRemoto } from "@/application/errors";
import { ClienteHttp } from "@/infra/http/cliente-http";
import {
  ClienteGatewayHttp,
  MetricasGatewayHttp,
  OrcamentoGatewayHttp,
  UsuarioGatewayHttp,
} from "@/infra/http/gateways-http";
import { ValorOrcado } from "@/domain/value-objects/valor-orcado";
import { NovoContato } from "@/domain/entities/novo-contato";

import { MAPA_DA_API } from "../domain/fixtures";

type Resposta = { status?: number; corpo?: unknown };

/** fetch falso que guarda as requisições e responde na ordem dada. */
function fetchFalso(...respostas: Resposta[]) {
  const fila = [...respostas];
  const chamadas: { url: string; metodo: string; corpo: unknown; headers: Headers }[] = [];
  const fn = vi.fn(async (url: string | URL | Request, init?: RequestInit) => {
    chamadas.push({
      url: String(url),
      metodo: init?.method ?? "GET",
      corpo: init?.body ? JSON.parse(String(init.body)) : undefined,
      headers: new Headers(init?.headers),
    });
    const { status = 200, corpo = null } = fila.shift() ?? {};
    return new Response(status === 204 ? null : JSON.stringify(corpo), { status });
  });
  return { fn: fn as typeof fetch, chamadas };
}

const CARD = {
  id: "o1",
  clienteId: "c1",
  clienteNome: "Maria",
  estagio: "ORCAMENTO_ENVIADO",
  valor: "4200.00",
  dataAbertura: "2026-09-01",
  qtdInteracoes: 2,
};

describe("ClienteHttp", () => {
  it("junta a base, manda JSON e o token", async () => {
    const { fn, chamadas } = fetchFalso({ corpo: { ok: true } });
    const http = new ClienteHttp("http://api/api/v1/", { fetch: fn, token: () => "abc" });

    await http.post("/clientes", { nome: "x" });

    expect(chamadas[0]).toMatchObject({ url: "http://api/api/v1/clientes", metodo: "POST", corpo: { nome: "x" } });
    expect(chamadas[0]?.headers.get("authorization")).toBe("Bearer abc");
    expect(chamadas[0]?.headers.get("content-type")).toBe("application/json");
  });

  it("transforma o erro padrão da API em ErroRemoto", async () => {
    const { fn } = fetchFalso({
      status: 422,
      corpo: { erro: "TransicaoInvalida", mensagem: "Sem valor", campo: "valor" },
    });

    const erro = await new ClienteHttp("/api", { fetch: fn }).get("/x").catch((e: unknown) => e);

    expect(erro).toBeInstanceOf(ErroRemoto);
    expect(erro).toMatchObject({ status: 422, codigo: "TransicaoInvalida", mensagem: "Sem valor", campo: "valor" });
  });

  it("erro sem corpo vira mensagem genérica", async () => {
    const { fn } = fetchFalso({ status: 500, corpo: "boom" });

    const erro = (await new ClienteHttp("/api", { fetch: fn }).get("/x").catch((e: unknown) => e)) as ErroRemoto;

    expect(erro.mensagem).toMatch(/servidor/i);
    expect(erro.sessaoExpirada).toBe(false);
  });

  it("401 indica sessão expirada", async () => {
    const { fn } = fetchFalso({ status: 401, corpo: { erro: "x", mensagem: "Faça login", campo: null } });

    const erro = (await new ClienteHttp("/api", { fetch: fn }).get("/x").catch((e: unknown) => e)) as ErroRemoto;

    expect(erro.sessaoExpirada).toBe(true);
  });

  it("falha de rede vira ErroRemoto offline", async () => {
    const fn = vi.fn(async () => {
      throw new TypeError("Failed to fetch");
    }) as unknown as typeof fetch;

    const erro = (await new ClienteHttp("/api", { fetch: fn }).get("/x").catch((e: unknown) => e)) as ErroRemoto;

    expect(erro.status).toBe(0);
    expect(erro.semConexao).toBe(true);
  });

  it("resposta 204 devolve undefined", async () => {
    const { fn } = fetchFalso({ status: 204 });

    expect(await new ClienteHttp("/api", { fetch: fn }).patch("/x", {})).toBeUndefined();
  });
});

describe("Gateways HTTP — rotas e mapeamento", () => {
  it("lista cards e converte o valor", async () => {
    // Formato real de GET /orcamentos: um objeto com os cards agrupados por estágio.
    const { fn, chamadas } = fetchFalso({
      corpo: {
        NOVO_CONTATO: [],
        EM_NEGOCIACAO: [],
        ORCAMENTO_ENVIADO: [CARD],
        FECHADO: [],
        PERDIDO: [{ ...CARD, id: "o2", estagio: "PERDIDO" }],
      },
    });

    const cards = await new OrcamentoGatewayHttp(new ClienteHttp("/api", { fetch: fn })).listarCards();
    const [card] = cards;

    expect(chamadas[0]?.url).toBe("/api/orcamentos");
    expect(cards.map((c) => c.id)).toEqual(["o1", "o2"]);
    expect(card?.valor?.centavos).toBe(420000);
    expect(card?.dataFechamento).toBeNull();
  });

  it("transições, mover, valor e interação", async () => {
    const atualizado = { ...CARD, estagio: "FECHADO", dataFechamento: "2026-09-15" };
    const { fn, chamadas } = fetchFalso(
      { corpo: MAPA_DA_API },
      { corpo: atualizado },
      { corpo: { ...atualizado, valor: null } },
      { status: 201, corpo: { id: "i1", tipo: "LIGACAO", conteudo: "Oi", dataHora: "2026-09-15T12:00:00Z" } },
    );
    const gateway = new OrcamentoGatewayHttp(new ClienteHttp("/api", { fetch: fn }));

    expect(await gateway.obterTransicoes()).toEqual(MAPA_DA_API);
    expect(await gateway.moverEstagio("o1", "FECHADO")).toEqual({
      estagio: "FECHADO",
      valor: ValorOrcado.deTexto("4200"),
      dataFechamento: "2026-09-15",
    });
    expect((await gateway.definirValor("o1", ValorOrcado.deTexto("10"))).valor).toBeNull();
    expect((await gateway.registrarInteracao("o1", "LIGACAO", "Oi")).tipo).toBe("LIGACAO");

    expect(chamadas.map((c) => `${c.metodo} ${c.url}`)).toEqual([
      "GET /api/orcamentos/transicoes",
      "PATCH /api/orcamentos/o1/estagio",
      "PATCH /api/orcamentos/o1/valor",
      "POST /api/orcamentos/o1/interacoes",
    ]);
    expect(chamadas[2]?.corpo).toEqual({ valor: "10.00" });
  });

  it("clientes: registrar, obter e histórico", async () => {
    const cliente = {
      id: "c1",
      nome: "Maria",
      telefone: "31998765432",
      email: "maria@x.com",
      empresa: null,
      tipoEmbalagemInteresse: null,
      criadoEm: "2026-09-01T10:00:00Z",
    };
    const orcamento = { id: "o1", clienteId: "c1", estagio: "NOVO_CONTATO", valor: null, dataAbertura: "2026-09-01", dataFechamento: null };
    const { fn, chamadas } = fetchFalso(
      { status: 201, corpo: { cliente, orcamento } },
      { corpo: { ...cliente, orcamentos: [orcamento] } },
      { corpo: [{ id: "i1", orcamentoId: "o1", tipo: "MENSAGEM", conteudo: "Oi", dataHora: "2026-09-02T10:00:00Z" }] },
    );
    const gateway = new ClienteGatewayHttp(new ClienteHttp("/api", { fetch: fn }));
    const valido = NovoContato.validar({ nome: "Maria", telefone: "31998765432", email: "maria@x.com" });
    if (!valido.ok) throw new Error("fixture inválida");

    const registrado = await gateway.registrarContato(valido.valor);
    const detalhe = await gateway.obterCliente("c1");
    const historico = await gateway.historico("c1");

    expect(registrado.orcamento.clienteNome).toBe("Maria");
    expect(chamadas[0]?.corpo).toEqual({
      nome: "Maria",
      telefone: "31998765432",
      email: "maria@x.com",
      empresa: null,
      tipoEmbalagemInteresse: null,
    });
    expect(detalhe.orcamentos[0]?.qtdInteracoes).toBe(0);
    expect(historico[0]?.orcamentoId).toBe("o1");
  });

  it("reabrir atendimento cria orçamento pelo cliente", async () => {
    const novo = {
      id: "o9",
      clienteId: "c1",
      estagio: "NOVO_CONTATO",
      valor: null,
      dataAbertura: "2026-10-01",
      dataFechamento: null,
    };
    const { fn, chamadas } = fetchFalso({ status: 201, corpo: novo });

    const orcamento = await new ClienteGatewayHttp(new ClienteHttp("/api", { fetch: fn })).reabrirAtendimento(
      "c1",
      "Maria",
    );

    expect(`${chamadas[0]?.metodo} ${chamadas[0]?.url}`).toBe("POST /api/clientes/c1/orcamentos");
    expect(orcamento).toMatchObject({ id: "o9", clienteNome: "Maria", estagio: "NOVO_CONTATO", qtdInteracoes: 0 });
  });

  it("métricas e usuários", async () => {
    const usuario = { id: "u1", nome: "Ana", email: "ana@crm.com", perfil: "USUARIO", ativo: true };
    const { fn, chamadas } = fetchFalso(
      { corpo: { emAberto: 3, fechados: 1, perdidos: 1, taxaFechamento: "50.00" } },
      { corpo: [usuario] },
      { status: 201, corpo: usuario },
      { corpo: { ...usuario, ativo: false } },
    );
    const http = new ClienteHttp("/api", { fetch: fn });
    const usuarios = new UsuarioGatewayHttp(http);

    expect((await new MetricasGatewayHttp(http).obter()).taxaFormatada()).toBe("50%");
    expect(await usuarios.listar()).toHaveLength(1);
    await usuarios.criar({ nome: "Ana", email: "ana@crm.com", senha: "12345678", perfil: "USUARIO" });
    expect((await usuarios.alterar("u1", { ativo: false })).ativo).toBe(false);
    expect(chamadas.map((c) => `${c.metodo} ${c.url}`)).toEqual([
      "GET /api/metricas/funil",
      "GET /api/usuarios",
      "POST /api/usuarios",
      "PATCH /api/usuarios/u1",
    ]);
  });
});
