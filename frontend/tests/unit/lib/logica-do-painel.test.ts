import type { Active, Over } from "@dnd-kit/core";
import { describe, expect, it } from "vitest";

import { montarColunas } from "@/application/use-cases/consultar-painel";
import {
  avisosDoArraste,
  destaqueDa,
  estagioDoDestino,
  filtrar,
} from "@/components/kanban/logica-do-painel";

import { funilPadrao, orcamento, VALOR } from "../domain/fixtures";

const funil = funilPadrao();
const maria = orcamento("EM_NEGOCIACAO", { id: "o1", clienteNome: "Maria José" });
const joao = orcamento("NOVO_CONTATO", { id: "o2", clienteNome: "João" });

describe("destaque das colunas durante o arraste", () => {
  it("sem arraste, nenhuma coluna se destaca", () => {
    expect(destaqueDa("FECHADO", null, funil)).toBeNull();
  });

  it("origem, destinos válidos e inválidos (inclui a guarda de valor)", () => {
    expect(destaqueDa("EM_NEGOCIACAO", maria, funil)).toBe("origem");
    expect(destaqueDa("PERDIDO", maria, funil)).toBe("valida");
    expect(destaqueDa("ORCAMENTO_ENVIADO", maria, funil)).toBe("invalida");
    expect(destaqueDa("ORCAMENTO_ENVIADO", orcamento("EM_NEGOCIACAO", { valor: VALOR }), funil)).toBe("valida");
    expect(destaqueDa("FECHADO", maria, funil)).toBe("invalida");
  });
});

describe("estagioDoDestino", () => {
  it("aceita só ids de coluna", () => {
    expect(estagioDoDestino("PERDIDO")).toBe("PERDIDO");
    expect(estagioDoDestino("o1")).toBeNull();
    expect(estagioDoDestino(undefined)).toBeNull();
  });
});

describe("filtrar", () => {
  const colunas = montarColunas([maria, joao]);

  it("busca sem acento e sem diferenciar maiúsculas", () => {
    const resultado = filtrar(colunas, "  JOSE ");

    expect(resultado.EM_NEGOCIACAO).toEqual([maria]);
    expect(resultado.NOVO_CONTATO).toEqual([]);
  });

  it("busca vazia devolve tudo", () => {
    expect(filtrar(colunas, " ")).toBe(colunas);
  });
});

describe("avisos para leitor de tela", () => {
  const avisos = avisosDoArraste(new Map([["o1", maria]]));
  const ativo = { id: "o1" } as Active;
  const sobre = (id: string) => ({ id }) as Over;

  it("narra o arraste em português", () => {
    expect(avisos.onDragStart({ active: ativo })).toBe("Movendo o orçamento de Maria José.");
    expect(avisos.onDragOver({ active: ativo, over: sobre("PERDIDO") })).toBe(
      "Maria José sobre a coluna Perdido.",
    );
    expect(avisos.onDragOver({ active: ativo, over: null })).toBeUndefined();
    expect(avisos.onDragEnd({ active: ativo, over: sobre("FECHADO") })).toBe(
      "Maria José solto na coluna Fechado.",
    );
    expect(avisos.onDragEnd({ active: ativo, over: null })).toBe("Maria José não foi movido.");
    expect(avisos.onDragCancel({ active: { id: "x" } as Active, over: null })).toBe(
      "Movimento de orçamento cancelado.",
    );
  });
});
