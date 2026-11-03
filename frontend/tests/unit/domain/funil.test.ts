import { describe, expect, it } from "vitest";

import { FormatoInvalido } from "@/domain/errors";
import { Funil } from "@/domain/funil/funil";
import { ESTAGIOS, type Estagio } from "@/domain/value-objects/estagio-atendimento";

import { funilPadrao, MAPA_DA_API } from "./fixtures";

describe("Funil — mapa de transições vindo da API (RN01)", () => {
  const funil = funilPadrao();

  it.each<[Estagio, Estagio[]]>([
    ["NOVO_CONTATO", ["EM_NEGOCIACAO", "PERDIDO"]],
    ["EM_NEGOCIACAO", ["ORCAMENTO_ENVIADO", "PERDIDO"]],
    ["ORCAMENTO_ENVIADO", ["FECHADO", "PERDIDO"]],
    ["FECHADO", []],
    ["PERDIDO", []],
  ])("de %s pode ir para %j", (origem, destinos) => {
    expect(funil.destinosDe(origem)).toEqual(destinos);
    for (const destino of ESTAGIOS) {
      expect(funil.podeMover(origem, destino)).toBe(destinos.includes(destino));
    }
  });

  it("estágios sem saída são terminais", () => {
    expect(ESTAGIOS.filter((e) => funil.ehTerminal(e))).toEqual(["FECHADO", "PERDIDO"]);
  });

  it("sabe quais estágios exigem valor (RN02)", () => {
    expect(ESTAGIOS.filter((e) => funil.exigeValor(e))).toEqual(["ORCAMENTO_ENVIADO", "FECHADO"]);
  });

  it("rejeita um mapa sem algum estágio", () => {
    const { PERDIDO: _ignorado, ...incompleto } = MAPA_DA_API.transicoes;
    expect(() => Funil.doMapa({ ...MAPA_DA_API, transicoes: incompleto })).toThrow(FormatoInvalido);
  });

  it("rejeita estágio desconhecido no mapa", () => {
    expect(() =>
      Funil.doMapa({
        ...MAPA_DA_API,
        transicoes: { ...MAPA_DA_API.transicoes, NOVO_CONTATO: ["ARQUIVADO"] },
      }),
    ).toThrow(FormatoInvalido);
    expect(() => Funil.doMapa({ ...MAPA_DA_API, exigemValor: ["ARQUIVADO"] })).toThrow(
      FormatoInvalido,
    );
  });
});
