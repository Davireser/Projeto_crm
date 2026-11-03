import { beforeEach, describe, expect, it } from "vitest";

import { AcessoNegado, ErroDeValidacao } from "@/application/errors";
import { GerenciarUsuarios } from "@/application/use-cases/gerenciar-usuarios";
import { Usuario } from "@/domain/entities/usuario";
import { OperacaoNaoPermitida } from "@/domain/errors";
import { UsuariosEmMemoria } from "@/infra/memoria/crm-em-memoria";

const admin = new Usuario({ id: "u1", nome: "Admin", email: "a@crm.com", perfil: "ADMINISTRADOR", ativo: true });
const ana = new Usuario({ id: "u2", nome: "Ana", email: "ana@crm.com", perfil: "USUARIO", ativo: true });

let usuarios: UsuariosEmMemoria;
let caso: GerenciarUsuarios;

beforeEach(() => {
  usuarios = new UsuariosEmMemoria([admin, ana]);
  caso = new GerenciarUsuarios(usuarios);
});

describe("GerenciarUsuarios (RF10, RNF07)", () => {
  it("admin lista usuários", async () => {
    expect(await caso.listar(admin)).toHaveLength(2);
  });

  it("usuário comum não gerencia", async () => {
    await expect(caso.listar(ana)).rejects.toThrow(AcessoNegado);
  });

  it("cria usuário validando nome, e-mail e senha", async () => {
    const criado = await caso.criar(admin, {
      nome: "Joana",
      email: "JOANA@crm.com",
      senha: "senha-forte",
      perfil: "USUARIO",
    });

    expect(criado.email).toBe("joana@crm.com");
  });

  it("reúne os erros do formulário de novo usuário", async () => {
    const erro = await caso
      .criar(admin, { nome: " ", email: "x", senha: "123", perfil: "USUARIO" })
      .catch((e: unknown) => e);

    expect(erro).toBeInstanceOf(ErroDeValidacao);
    expect(Object.keys((erro as ErroDeValidacao).erros).sort()).toEqual(["email", "nome", "senha"]);
  });

  it("desativa outro usuário e muda o perfil", async () => {
    expect((await caso.alterar(admin, ana, { ativo: false })).ativo).toBe(false);
    expect((await caso.alterar(admin, ana, { perfil: "ADMINISTRADOR" })).perfil).toBe(
      "ADMINISTRADOR",
    );
  });

  it("admin não altera a própria conta", async () => {
    await expect(caso.alterar(admin, admin, { ativo: false })).rejects.toThrow(
      OperacaoNaoPermitida,
    );
  });
});
