import { describe, expect, it } from "vitest";

import { Interacao } from "@/domain/entities/interacao";
import { NovoContato } from "@/domain/entities/novo-contato";
import { Usuario } from "@/domain/entities/usuario";
import { FormatoInvalido } from "@/domain/errors";

describe("NovoContato — cadastro de cliente (RF01, RF09)", () => {
  const valido = {
    nome: "  Maria Souza ",
    telefone: "(31) 99876-5432",
    email: "Maria@X.com",
    empresa: " Embalagens ABC ",
    tipoEmbalagemInteresse: "",
  };

  it("valida e normaliza os dados", () => {
    const resultado = NovoContato.validar(valido);

    expect(resultado.ok).toBe(true);
    if (!resultado.ok) return;
    expect(resultado.valor.nome).toBe("Maria Souza");
    expect(resultado.valor.telefone.numero).toBe("31998765432");
    expect(resultado.valor.email.endereco).toBe("maria@x.com");
    expect(resultado.valor.empresa).toBe("Embalagens ABC");
    expect(resultado.valor.tipoEmbalagemInteresse).toBeNull();
  });

  it("reúne todos os erros por campo de uma vez", () => {
    const resultado = NovoContato.validar({ nome: " ", telefone: "123", email: "x" });

    expect(resultado.ok).toBe(false);
    if (resultado.ok) return;
    expect(Object.keys(resultado.erros).sort()).toEqual(["email", "nome", "telefone"]);
    expect(resultado.erros.nome).toBe("O nome do cliente é obrigatório.");
  });
});

describe("Interacao", () => {
  it("exige conteúdo", () => {
    expect(() => Interacao.validarConteudo("   ")).toThrow(FormatoInvalido);
    expect(Interacao.validarConteudo("  Ligou ")).toBe("Ligou");
  });

  it("guarda os dados e é imutável", () => {
    const interacao = new Interacao({
      id: "i1",
      tipo: "LIGACAO",
      conteudo: "Pediu 500 caixas",
      dataHora: "2026-09-15T14:30:00Z",
    });

    expect(interacao.tipo).toBe("LIGACAO");
    expect(Object.isFrozen(interacao)).toBe(true);
  });
});

describe("Usuario — perfis (RF10, RNF07)", () => {
  const admin = new Usuario({
    id: "u1",
    nome: "Admin",
    email: "admin@crm.com",
    perfil: "ADMINISTRADOR",
    ativo: true,
  });
  const ana = new Usuario({
    id: "u2",
    nome: "Ana",
    email: "ana@crm.com",
    perfil: "USUARIO",
    ativo: true,
  });

  it("só administrador ativo gerencia usuários", () => {
    expect(admin.podeGerenciarUsuarios()).toBe(true);
    expect(ana.podeGerenciarUsuarios()).toBe(false);
    expect(new Usuario({ ...admin, ativo: false }).podeGerenciarUsuarios()).toBe(false);
  });

  it("administrador não desativa nem rebaixa a si mesmo", () => {
    expect(admin.podeAlterarStatusDe(ana)).toBe(true);
    expect(admin.podeAlterarStatusDe(admin)).toBe(false);
    expect(ana.podeAlterarStatusDe(admin)).toBe(false);
  });

  it("nome exige conteúdo", () => {
    expect(() => new Usuario({ ...ana, nome: " " })).toThrow(FormatoInvalido);
  });
});
