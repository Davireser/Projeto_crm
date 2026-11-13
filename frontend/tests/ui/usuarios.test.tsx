import { screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import { ErroRemoto } from "@/application/errors";
import { GestaoUsuarios } from "@/components/usuarios/gestao-usuarios";
import { Usuario, type DadosUsuario } from "@/domain/entities/usuario";
import { UsuariosEmMemoria } from "@/infra/memoria/crm-em-memoria";

import { apiDeMemoria, novoCrm, renderComApi } from "./apoio";

const ADMIN: DadosUsuario = { id: "u1", nome: "Davi", email: "davi@crm.com", perfil: "ADMINISTRADOR", ativo: true };
const ANA: DadosUsuario = { id: "u2", nome: "Ana", email: "ana@crm.com", perfil: "USUARIO", ativo: true };

function renderizar(usuarios = new UsuariosEmMemoria([new Usuario(ADMIN), new Usuario(ANA)])) {
  const api = { ...apiDeMemoria(novoCrm()), usuarios };
  renderComApi(<GestaoUsuarios solicitante={ADMIN} />, api);
  return usuarios;
}

const linha = async (nome: string) => (await screen.findByRole("cell", { name: nome })).closest("tr")!;

describe("Gestão de usuários (RF10)", () => {
  it("lista usuários com perfil e situação; a própria conta não tem ações", async () => {
    renderizar();

    const davi = await linha("Davi");
    expect(within(davi).getByText("Você")).toBeInTheDocument();
    expect(within(davi).queryByRole("button")).not.toBeInTheDocument();
    const ana = await linha("Ana");
    expect(within(ana).getByText("Usuário")).toBeInTheDocument();
    expect(within(ana).getByText("Ativo")).toBeInTheDocument();
  });

  it("desativa e reativa outro usuário", async () => {
    renderizar();
    const ana = await linha("Ana");

    await userEvent.click(within(ana).getByRole("button", { name: "Desativar Ana" }));

    expect(await within(ana).findByText("Inativo")).toBeInTheDocument();
    expect(await screen.findByText("Acesso de Ana desativado.")).toBeInTheDocument();
    await userEvent.click(within(ana).getByRole("button", { name: "Ativar Ana" }));
    expect(await within(ana).findByText("Ativo")).toBeInTheDocument();
  });

  it("cria usuário mostrando todos os erros antes e enviando depois", async () => {
    const usuarios = renderizar();
    await userEvent.click(await screen.findByRole("button", { name: "Novo usuário" }));
    const gaveta = await screen.findByRole("dialog");

    await userEvent.click(within(gaveta).getByRole("button", { name: "Criar usuário" }));
    expect(within(gaveta).getByLabelText("Nome")).toHaveAccessibleDescription("O nome do usuário é obrigatório.");
    expect(within(gaveta).getByLabelText("Senha")).toHaveAccessibleDescription(/pelo menos 8/);

    await userEvent.type(within(gaveta).getByLabelText("Nome"), "Joana");
    await userEvent.type(within(gaveta).getByLabelText("E-mail"), "joana@crm.com");
    await userEvent.type(within(gaveta).getByLabelText("Senha"), "senha-forte");
    await userEvent.click(within(gaveta).getByRole("radio", { name: "Administrador" }));
    await userEvent.click(within(gaveta).getByRole("button", { name: "Criar usuário" }));

    const joana = await linha("Joana");
    expect(within(joana).getByText("Administrador")).toBeInTheDocument();
    expect((await usuarios.listar()).map((u) => u.email)).toContain("joana@crm.com");
  });

  it("e-mail já cadastrado: o erro da API aparece no campo", async () => {
    const usuarios = new UsuariosEmMemoria([new Usuario(ADMIN)]);
    usuarios.criar = () =>
      Promise.reject(new ErroRemoto(409, "EmailJaCadastrado", "E-mail já cadastrado.", "email"));
    renderizar(usuarios);
    await userEvent.click(await screen.findByRole("button", { name: "Novo usuário" }));
    const gaveta = await screen.findByRole("dialog");

    await userEvent.type(within(gaveta).getByLabelText("Nome"), "Joana");
    await userEvent.type(within(gaveta).getByLabelText("E-mail"), "davi@crm.com");
    await userEvent.type(within(gaveta).getByLabelText("Senha"), "senha-forte");
    await userEvent.click(within(gaveta).getByRole("button", { name: "Criar usuário" }));

    expect(await within(gaveta).findByText("E-mail já cadastrado.")).toBeInTheDocument();
    expect(within(gaveta).getByLabelText("E-mail")).toHaveAttribute("aria-invalid", "true");
  });

  it("edita nome, e-mail e perfil", async () => {
    renderizar();
    await userEvent.click(within(await linha("Ana")).getByRole("button", { name: "Editar Ana" }));
    const gaveta = await screen.findByRole("dialog");

    const nome = within(gaveta).getByLabelText("Nome");
    await userEvent.clear(nome);
    await userEvent.type(nome, "Ana Paula");
    await userEvent.click(within(gaveta).getByRole("radio", { name: "Administrador" }));
    await userEvent.click(within(gaveta).getByRole("button", { name: "Salvar alterações" }));

    const ana = await linha("Ana Paula");
    expect(within(ana).getByText("Administrador")).toBeInTheDocument();
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });
});
