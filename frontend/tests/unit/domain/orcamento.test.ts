import { describe, expect, it } from "vitest";

import { TransicaoInvalida } from "@/domain/errors";
import { ValorOrcado } from "@/domain/value-objects/valor-orcado";

import { funilPadrao, HOJE, orcamento, VALOR } from "./fixtures";

const funil = funilPadrao();

describe("Orcamento — mover estágio (RF02, RF03, RN01–RN03)", () => {
  it("move para um estágio permitido devolvendo um novo orçamento", () => {
    const original = orcamento("NOVO_CONTATO");

    const movido = original.moverPara("EM_NEGOCIACAO", funil, HOJE);

    expect(movido.estagio).toBe("EM_NEGOCIACAO");
    expect(movido.id).toBe(original.id);
    expect(original.estagio).toBe("NOVO_CONTATO");
  });

  it("rejeita salto de etapa com mensagem clara", () => {
    expect(() => orcamento("NOVO_CONTATO").moverPara("FECHADO", funil, HOJE)).toThrow(
      new TransicaoInvalida("Não é possível mover de Novo contato para Fechado.", "estagio"),
    );
  });

  it("não envia orçamento sem valor (RN02)", () => {
    const erro = capturar(() =>
      orcamento("EM_NEGOCIACAO").moverPara("ORCAMENTO_ENVIADO", funil, HOJE),
    );

    expect(erro).toBeInstanceOf(TransicaoInvalida);
    expect(erro).toMatchObject({ campo: "valor" });
  });

  it("com valor, envia e depois fecha preenchendo a data de fechamento (RN03)", () => {
    const fechado = orcamento("EM_NEGOCIACAO", { valor: VALOR })
      .moverPara("ORCAMENTO_ENVIADO", funil, HOJE)
      .moverPara("FECHADO", funil, HOJE);

    expect(fechado.estagio).toBe("FECHADO");
    expect(fechado.dataFechamento).toBe(HOJE);
    expect(fechado.estaEmAberto(funil)).toBe(false);
  });

  it("perder não exige valor", () => {
    const perdido = orcamento("NOVO_CONTATO").moverPara("PERDIDO", funil, HOJE);

    expect(perdido.dataFechamento).toBe(HOJE);
  });

  it("estágio ativo continua sem data de fechamento", () => {
    expect(orcamento().moverPara("EM_NEGOCIACAO", funil, HOJE).dataFechamento).toBeNull();
    expect(orcamento().estaEmAberto(funil)).toBe(true);
  });

  it("explica o motivo de um movimento inválido sem lançar", () => {
    expect(orcamento("NOVO_CONTATO").motivoParaNaoMover("EM_NEGOCIACAO", funil)).toBeNull();
    expect(orcamento("NOVO_CONTATO").motivoParaNaoMover("FECHADO", funil)).toMatch(/Não é possível/);
  });
});

describe("Orcamento — valor", () => {
  it("define o valor enquanto aberto", () => {
    const novo = ValorOrcado.deTexto("3900");

    expect(orcamento("EM_NEGOCIACAO").definirValor(novo, funil).valor).toBe(novo);
  });

  it("não altera o valor depois de encerrado", () => {
    expect(() =>
      orcamento("FECHADO", { valor: VALOR }).definirValor(ValorOrcado.deTexto("1"), funil),
    ).toThrow(TransicaoInvalida);
  });
});

describe("Orcamento — interações", () => {
  it("conta uma nova interação", () => {
    expect(orcamento().comNovaInteracao().qtdInteracoes).toBe(1);
  });

  it("é imutável", () => {
    expect(Object.isFrozen(orcamento())).toBe(true);
  });
});

function capturar(acao: () => unknown): unknown {
  try {
    acao();
  } catch (erro) {
    return erro;
  }
  throw new Error("esperava uma exceção");
}

describe("Orcamento — reabrir atendimento", () => {
  it("só um orçamento perdido permite reabrir o atendimento do cliente", () => {
    expect(orcamento("PERDIDO").podeReabrirAtendimento()).toBe(true);
    expect(orcamento("FECHADO").podeReabrirAtendimento()).toBe(false);
    expect(orcamento("NOVO_CONTATO").podeReabrirAtendimento()).toBe(false);
  });
});
