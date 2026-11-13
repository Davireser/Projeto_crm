import { describe, expect, it } from "vitest";

import { FormatoInvalido, ValorInvalido } from "@/domain/errors";
import { Email } from "@/domain/value-objects/email";
import { ESTAGIOS, EstagioAtendimento, rotuloDoEstagio } from "@/domain/value-objects/estagio-atendimento";
import { Telefone } from "@/domain/value-objects/telefone";
import { TIPOS_DE_INTERACAO, rotuloDoTipo } from "@/domain/value-objects/tipo-interacao";
import { ValorOrcado } from "@/domain/value-objects/valor-orcado";

describe("Email (RN05)", () => {
  it("normaliza para minúsculas e sem espaços", () => {
    expect(Email.criar("  Maria@Empresa.COM.br ").endereco).toBe("maria@empresa.com.br");
  });

  it.each(["", "maria", "maria@", "@x.com", "maria@x", "maria@x.c", "ma ria@x.com"])(
    "rejeita %j",
    (texto) => {
      expect(() => Email.criar(texto)).toThrow(FormatoInvalido);
    },
  );

  it("informa o campo do erro", () => {
    try {
      Email.criar("x");
    } catch (erro) {
      expect(erro).toMatchObject({ campo: "email" });
    }
  });

  it("compara por valor", () => {
    expect(Email.criar("a@b.com").igualA(Email.criar("A@B.com"))).toBe(true);
    expect(Email.criar("a@b.com").igualA(Email.criar("c@b.com"))).toBe(false);
  });
});

describe("Telefone (RN04)", () => {
  it.each([
    ["(31) 99876-5432", "31998765432"],
    ["+31 3456.7890", "3134567890"],
    ["11 3456-7890", "1134567890"],
  ])("aceita %j e guarda só os dígitos", (texto, digitos) => {
    expect(Telefone.criar(texto).numero).toBe(digitos);
  });

  it.each(["", "123", "01998765432", "31898765432", "3119876543", "319987654321", "31abc"])(
    "rejeita %j",
    (texto) => {
      expect(() => Telefone.criar(texto)).toThrow(FormatoInvalido);
    },
  );

  it("formata celular e fixo", () => {
    expect(Telefone.criar("31998765432").formatado()).toBe("(31) 99876-5432");
    expect(Telefone.criar("1134567890").formatado()).toBe("(11) 3456-7890");
  });
});

describe("ValorOrcado (RN06)", () => {
  it.each([
    ["4200", 420000],
    ["4200.5", 420050],
    ["4.200,50", 420050],
    ["R$ 1.234.567,89", 123456789],
    ["0,01", 1],
    // Ponto com três dígitos depois é separador de milhar, como se escreve no Brasil.
    ["12.500", 1250000],
    ["1.234.567", 123456700],
    ["4.20", 420],
  ])("lê %j", (texto, centavos) => {
    expect(ValorOrcado.deTexto(texto).centavos).toBe(centavos);
  });

  it.each(["0", "-10", "abc", "", "10,555", "1.2.3,4,5"])("rejeita %j", (texto) => {
    expect(() => ValorOrcado.deTexto(texto)).toThrow(ValorInvalido);
  });

  it("rejeita centavos não inteiros ou não positivos", () => {
    expect(() => ValorOrcado.deCentavos(0)).toThrow(ValorInvalido);
    expect(() => ValorOrcado.deCentavos(10.5)).toThrow(ValorInvalido);
    expect(() => ValorOrcado.deCentavos(Number.NaN)).toThrow(ValorInvalido);
  });

  it("converte para o decimal que a API espera", () => {
    expect(ValorOrcado.deTexto("4.200,5").paraApi()).toBe("4200.50");
    expect(ValorOrcado.deCentavos(7).paraApi()).toBe("0.07");
  });

  it("mostra para edição no formato brasileiro, que o próprio deTexto lê de volta", () => {
    const valor = ValorOrcado.deTexto("12500");
    expect(valor.paraEdicao()).toBe("12.500,00");
    expect(ValorOrcado.deTexto(valor.paraEdicao()).igualA(valor)).toBe(true);
  });

  it("formata em reais", () => {
    expect(ValorOrcado.deTexto("4200.5").formatado()).toBe("R$ 4.200,50");
  });

  it("compara por valor", () => {
    expect(ValorOrcado.deTexto("10").igualA(ValorOrcado.deCentavos(1000))).toBe(true);
  });
});

describe("EstagioAtendimento e TipoInteracao", () => {
  it("lista os cinco estágios na ordem do funil", () => {
    expect(ESTAGIOS).toEqual([
      "NOVO_CONTATO",
      "EM_NEGOCIACAO",
      "ORCAMENTO_ENVIADO",
      "FECHADO",
      "PERDIDO",
    ]);
  });

  it("tem rótulo em português para cada estágio", () => {
    expect(rotuloDoEstagio(EstagioAtendimento.ORCAMENTO_ENVIADO)).toBe("Orçamento enviado");
    expect(ESTAGIOS.map(rotuloDoEstagio).every((r) => r.length > 0)).toBe(true);
  });

  it("reconhece estágios válidos", () => {
    expect(EstagioAtendimento.eh("FECHADO")).toBe(true);
    expect(EstagioAtendimento.eh("ARQUIVADO")).toBe(false);
  });

  it("tem rótulo para cada tipo de interação", () => {
    expect(TIPOS_DE_INTERACAO).toEqual(["MENSAGEM", "LIGACAO", "REUNIAO"]);
    expect(rotuloDoTipo("LIGACAO")).toBe("Ligação");
  });
});
