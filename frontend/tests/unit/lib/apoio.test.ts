import { describe, expect, it } from "vitest";

import { ErroDeValidacao, ErroRemoto } from "@/application/errors";
import { ValorInvalido } from "@/domain/errors";
import { paraCardDto, paraOrcamento } from "@/infra/http/mapeadores";
import { formatarData, formatarDataHora, hojeNoNegocio } from "@/lib/datas";
import { errosDoFormulario, mensagemDeErro } from "@/lib/mensagens";

import { orcamento, VALOR } from "../domain/fixtures";

describe("datas no fuso do negócio (America/Sao_Paulo)", () => {
  it("hoje considera o fuso: 01h UTC ainda é o dia anterior em São Paulo", () => {
    expect(hojeNoNegocio(new Date("2026-09-16T01:00:00Z"))).toBe("2026-09-15");
    expect(hojeNoNegocio(new Date("2026-09-16T12:00:00Z"))).toBe("2026-09-16");
  });

  it("formata data ISO sem deslocar o dia", () => {
    expect(formatarData("2026-09-01")).toBe("01/09/2026");
  });

  it("formata instante UTC no horário de São Paulo", () => {
    expect(formatarDataHora("2026-09-15T14:30:00Z")).toBe("15/09/2026, 11:30");
  });
});

describe("mensagemDeErro", () => {
  it("usa a mensagem do domínio ou da API", () => {
    expect(mensagemDeErro(new ValorInvalido("Valor ruim", "valor"))).toBe("Valor ruim");
    expect(mensagemDeErro(new ErroRemoto(422, "X", "Recusado"))).toBe("Recusado");
  });

  it("erro desconhecido vira mensagem genérica", () => {
    expect(mensagemDeErro(new Error("stack interno"))).toBe("Algo deu errado. Tente de novo.");
  });
});

describe("errosDoFormulario", () => {
  it("validação local: um erro por campo", () => {
    expect(errosDoFormulario(new ErroDeValidacao({ nome: "Obrigatório" }))).toEqual({ nome: "Obrigatório" });
  });

  it("erro da API vai para o campo indicado, ou para o geral", () => {
    expect(errosDoFormulario(new ErroRemoto(422, "X", "E-mail recusado", "email"))).toEqual({
      email: "E-mail recusado",
    });
    expect(errosDoFormulario(new ErroRemoto(0, "SemConexao", "Sem conexão"))).toEqual({ geral: "Sem conexão" });
    expect(errosDoFormulario(new Error("x"))).toEqual({ geral: "Algo deu errado. Tente de novo." });
  });
});

describe("paraCardDto", () => {
  it("faz o caminho de volta para o JSON da API (cache offline)", () => {
    const card = orcamento("FECHADO", { valor: VALOR, dataFechamento: "2026-09-15", qtdInteracoes: 2 });

    const dto = paraCardDto(card);

    expect(dto).toEqual({
      id: "orc-1",
      clienteId: "cli-1",
      clienteNome: "Maria",
      estagio: "FECHADO",
      valor: "4200.00",
      dataAbertura: "2026-09-01",
      dataFechamento: "2026-09-15",
      qtdInteracoes: 2,
    });
    expect(paraOrcamento(JSON.parse(JSON.stringify(dto)))).toEqual(card);
  });

  it("sem valor vira null", () => {
    expect(paraCardDto(orcamento()).valor).toBeNull();
  });
});
