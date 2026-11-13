import { beforeEach, describe, expect, it } from "vitest";

import { ConsultarCliente } from "@/application/use-cases/consultar-cliente";
import { ConsultarMetricas } from "@/application/use-cases/consultar-metricas";
import { ConsultarPainel, montarColunas } from "@/application/use-cases/consultar-painel";
import { DefinirValor } from "@/application/use-cases/definir-valor";
import { MoverEstagio } from "@/application/use-cases/mover-estagio";
import { ReabrirAtendimento } from "@/application/use-cases/reabrir-atendimento";
import { RegistrarContato } from "@/application/use-cases/registrar-contato";
import { RegistrarInteracao } from "@/application/use-cases/registrar-interacao";
import { ErroDeValidacao } from "@/application/errors";
import {
  FormatoInvalido,
  OperacaoNaoPermitida,
  TransicaoInvalida,
  ValorInvalido,
} from "@/domain/errors";
import { MetricasFunil } from "@/domain/entities/metricas-funil";
import type { Estagio } from "@/domain/value-objects/estagio-atendimento";
import { ValorOrcado, formatarCentavos } from "@/domain/value-objects/valor-orcado";
import { CrmEmMemoria } from "@/infra/memoria/crm-em-memoria";

import { MAPA_DA_API } from "../domain/fixtures";

const MARIA = {
  nome: "Maria",
  telefone: "31998765432",
  email: "maria@x.com",
};

let crm: CrmEmMemoria;

beforeEach(() => {
  crm = new CrmEmMemoria(MAPA_DA_API, () => new Date("2026-09-15T12:00:00Z"));
});

async function contatoRegistrado(dados: Partial<typeof MARIA> = {}) {
  return new RegistrarContato(crm.clientes).executar({ ...MARIA, ...dados });
}

describe("RegistrarContato (RF01, RF09)", () => {
  it("cria cliente e orçamento em Novo contato", async () => {
    const { clienteId, orcamento } = await contatoRegistrado();

    expect(orcamento.estagio).toBe("NOVO_CONTATO");
    expect(orcamento.clienteId).toBe(clienteId);
    expect(orcamento.clienteNome).toBe("Maria");
  });

  it("não chama a API se os dados são inválidos e devolve os erros por campo", async () => {
    const erro = await new RegistrarContato(crm.clientes)
      .executar({ nome: "", telefone: "1", email: "x" })
      .catch((e: unknown) => e);

    expect(erro).toBeInstanceOf(ErroDeValidacao);
    expect((erro as ErroDeValidacao).erros).toHaveProperty("telefone");
    expect(await crm.orcamentos.listarCards()).toEqual([]);
  });
});

describe("ConsultarPainel (RF05)", () => {
  it("agrupa os cards nas cinco colunas e entrega o funil", async () => {
    await contatoRegistrado();

    const { colunas, funil } = await new ConsultarPainel(crm.orcamentos).executar();

    expect(colunas.NOVO_CONTATO).toHaveLength(1);
    expect(colunas.FECHADO).toEqual([]);
    expect(funil.podeMover("NOVO_CONTATO", "EM_NEGOCIACAO")).toBe(true);
  });

  it("montarColunas cria todas as colunas mesmo vazias", () => {
    expect(Object.keys(montarColunas([]))).toHaveLength(5);
  });
});

describe("MoverEstagio (RF02, RF03)", () => {
  it("valida no domínio e confirma na API", async () => {
    const { orcamento } = await contatoRegistrado();
    const { funil } = await new ConsultarPainel(crm.orcamentos).executar();

    const movido = await new MoverEstagio(crm.orcamentos).executar(orcamento, "EM_NEGOCIACAO", funil);

    expect(movido.estagio).toBe("EM_NEGOCIACAO");
    expect(movido.clienteNome).toBe("Maria");
    expect((await crm.orcamentos.listarCards())[0]?.estagio).toBe("EM_NEGOCIACAO");
  });

  it("transição inválida nem chega na API", async () => {
    const { orcamento } = await contatoRegistrado();
    const { funil } = await new ConsultarPainel(crm.orcamentos).executar();

    await expect(
      new MoverEstagio(crm.orcamentos).executar(orcamento, "FECHADO", funil),
    ).rejects.toThrow(TransicaoInvalida);
    expect(crm.orcamentos.chamadas).toEqual([]);
  });
});

describe("DefinirValor", () => {
  it("lê o texto digitado e grava o valor", async () => {
    const { orcamento } = await contatoRegistrado();
    const { funil } = await new ConsultarPainel(crm.orcamentos).executar();

    const comValor = await new DefinirValor(crm.orcamentos).executar(orcamento, "4.200,50", funil);

    expect(comValor.valor?.paraApi()).toBe("4200.50");
  });

  it("valor inválido é recusado antes da API", async () => {
    const { orcamento } = await contatoRegistrado();
    const { funil } = await new ConsultarPainel(crm.orcamentos).executar();

    await expect(
      new DefinirValor(crm.orcamentos).executar(orcamento, "-3", funil),
    ).rejects.toThrow(ValorInvalido);
  });
});

describe("RegistrarInteracao (RF04)", () => {
  it("registra com conteúdo limpo", async () => {
    const { orcamento } = await contatoRegistrado();

    const interacao = await new RegistrarInteracao(crm.orcamentos).executar(
      orcamento.id,
      "LIGACAO",
      "  Pediu 500 caixas ",
    );

    expect(interacao.conteudo).toBe("Pediu 500 caixas");
    expect(interacao.dataHora).toBe("2026-09-15T12:00:00.000Z");
  });

  it("conteúdo vazio é recusado", async () => {
    await expect(
      new RegistrarInteracao(crm.orcamentos).executar("x", "MENSAGEM", " "),
    ).rejects.toThrow(FormatoInvalido);
  });
});

describe("ConsultarCliente (RF07, RF08)", () => {
  it("junta cliente, orçamentos com nº de interações e a linha do tempo", async () => {
    const { clienteId, orcamento } = await contatoRegistrado();
    await new RegistrarInteracao(crm.orcamentos).executar(orcamento.id, "MENSAGEM", "Oi");

    const detalhe = await new ConsultarCliente(crm.clientes).executar(clienteId);

    expect(detalhe.cliente.nome).toBe("Maria");
    expect(detalhe.cliente.telefone.formatado()).toBe("(31) 99876-5432");
    expect(detalhe.orcamentos[0]?.qtdInteracoes).toBe(1);
    expect(detalhe.historico.map((h) => h.interacao.conteudo)).toEqual(["Oi"]);
  });
});

describe("ConsultarMetricas (RF06)", () => {
  it("calcula a taxa de fechamento", async () => {
    await contatoRegistrado();

    const metricas = await new ConsultarMetricas(crm.metricas).executar();

    expect(metricas.emAberto).toBe(1);
    expect(metricas.taxaFormatada()).toBe("—");
  });

  it("soma o dinheiro de cada estágio; orçamento sem valor só conta como 'sem valor'", async () => {
    const { orcamento } = await contatoRegistrado();
    await contatoRegistrado({ email: "outra@x.com" });
    await crm.orcamentos.definirValor(orcamento.id, ValorOrcado.deTexto("1.500,50"));

    const metricas = await new ConsultarMetricas(crm.metricas).executar();

    expect(metricas.porEstagio.map((t) => t.estagio)).toEqual([
      "NOVO_CONTATO", "EM_NEGOCIACAO", "ORCAMENTO_ENVIADO", "FECHADO", "PERDIDO",
    ]);
    expect(metricas.porEstagio[0]).toEqual({ estagio: "NOVO_CONTATO", quantidade: 2, valorCentavos: 150050, semValor: 1 });
    expect(metricas.valorEmAberto()).toBe(150050);
  });
});

describe("MetricasFunil", () => {
  const total = (estagio: Estagio, valorCentavos: number) => ({ estagio, quantidade: 1, valorCentavos, semValor: 0 });

  it("dinheiro em aberto ignora fechados e perdidos; maior estágio serve de escala para as barras", () => {
    const metricas = new MetricasFunil({
      emAberto: 2, fechados: 1, perdidos: 1, taxaFechamento: 50,
      porEstagio: [total("NOVO_CONTATO", 100), total("EM_NEGOCIACAO", 200), total("FECHADO", 900), total("PERDIDO", 50)],
    });

    expect(metricas.valorEmAberto()).toBe(300);
    expect(metricas.maiorValorDeEstagio()).toBe(900);
  });

  it("dados antigos (sem porEstagio) não quebram", () => {
    const metricas = new MetricasFunil({ emAberto: 0, fechados: 0, perdidos: 0, taxaFechamento: null } as never);

    expect(metricas.porEstagio).toEqual([]);
    expect(metricas.valorEmAberto()).toBe(0);
    expect(metricas.maiorValorDeEstagio()).toBe(0);
  });
});

describe("formatarCentavos", () => {
  it("formata em reais, inclusive zero", () => {
    expect(formatarCentavos(0)).toMatch(/^R\$\s0,00$/);
    expect(formatarCentavos(1250000)).toMatch(/^R\$\s12\.500,00$/);
  });
});

describe("ReabrirAtendimento", () => {
  it("cliente perdido volta ao funil com um novo orçamento; o perdido continua lá", async () => {
    const { orcamento } = await contatoRegistrado();
    await crm.orcamentos.moverEstagio(orcamento.id, "PERDIDO");
    const perdido = crm.orcamento(orcamento.id);

    const novo = await new ReabrirAtendimento(crm.clientes).executar(perdido);

    expect(novo.id).not.toBe(perdido.id);
    expect(novo).toMatchObject({ clienteId: perdido.clienteId, clienteNome: "Maria", estagio: "NOVO_CONTATO" });
    expect(crm.orcamento(perdido.id).estagio).toBe("PERDIDO");
  });

  it("orçamento que não está perdido nem chega na API", async () => {
    const { orcamento } = await contatoRegistrado();

    await expect(new ReabrirAtendimento(crm.clientes).executar(orcamento)).rejects.toThrow(
      OperacaoNaoPermitida,
    );
    expect(crm.orcamentosSalvos.size).toBe(1);
  });

  it("como no backend, não reabre quem ainda tem orçamento em aberto", async () => {
    const { orcamento } = await contatoRegistrado();
    await crm.orcamentos.moverEstagio(orcamento.id, "PERDIDO");
    const perdido = crm.orcamento(orcamento.id);
    await new ReabrirAtendimento(crm.clientes).executar(perdido);

    await expect(new ReabrirAtendimento(crm.clientes).executar(perdido)).rejects.toThrow(
      "Maria já tem um orçamento em aberto.",
    );
  });
});
