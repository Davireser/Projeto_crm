import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ErroRemoto } from "@/application/errors";
import { FormNovoContato } from "@/components/contatos/form-novo-contato";
import { CHAVE_PAINEL } from "@/hooks/use-painel";
import type { PainelDto } from "@/lib/api/api-navegador";

import { MAPA_DA_API } from "../unit/domain/fixtures";
import { apiDeMemoria, novoCrm, renderComApi } from "./apoio";

const push = vi.fn();
vi.mock("next/navigation", () => ({ useRouter: () => ({ push }) }));

beforeEach(() => push.mockReset());

async function preencher(campos: Partial<Record<string, string>>) {
  const usuario = userEvent.setup();
  for (const [rotulo, valor] of Object.entries(campos)) {
    if (valor) await usuario.type(screen.getByLabelText(new RegExp(`^${rotulo}`)), valor);
  }
  await usuario.click(screen.getByRole("button", { name: "Registrar contato" }));
  return usuario;
}

describe("Novo contato (RF01, RF09)", () => {
  it("mostra todos os erros juntos e não chama a API", async () => {
    const crm = novoCrm();
    renderComApi(<FormNovoContato />, apiDeMemoria(crm));

    await preencher({ Telefone: "123", "E-mail": "maria@" });

    expect(screen.getByLabelText(/^Nome/)).toHaveAccessibleDescription("O nome do cliente é obrigatório.");
    expect(screen.getByLabelText(/^Telefone/)).toHaveAccessibleDescription(/Telefone inválido/);
    expect(screen.getByLabelText(/^E-mail/)).toHaveAttribute("aria-invalid", "true");
    expect(screen.getByLabelText(/^Nome/)).toHaveFocus();
    expect(crm.clientesSalvos.size).toBe(0);
  });

  it("corrigir um campo apaga o erro dele", async () => {
    renderComApi(<FormNovoContato />, apiDeMemoria(novoCrm()));
    const usuario = await preencher({});

    await usuario.type(screen.getByLabelText(/^Nome/), "M");

    expect(screen.getByLabelText(/^Nome/)).not.toHaveAttribute("aria-invalid", "true");
    expect(screen.getByLabelText(/^Telefone/)).toHaveAttribute("aria-invalid", "true");
  });

  it("registra, coloca o card no painel e volta para o Kanban", async () => {
    const crm = novoCrm();
    const { queryClient } = renderComApi(<FormNovoContato />, apiDeMemoria(crm));
    queryClient.setQueryData<PainelDto>(CHAVE_PAINEL, { cards: [], mapa: MAPA_DA_API });

    await preencher({
      Nome: "Maria Souza",
      Telefone: "(31) 99876-5432",
      "E-mail": "maria@abc.com.br",
      Empresa: "Embalagens ABC",
    });

    await waitFor(() => expect(push).toHaveBeenCalledWith("/painel"));
    const [cliente] = crm.clientesSalvos.values();
    expect(cliente?.telefone.numero).toBe("31998765432");
    expect(cliente?.empresa).toBe("Embalagens ABC");
    expect(cliente?.tipoEmbalagemInteresse).toBeNull();
    expect(queryClient.getQueryData<PainelDto>(CHAVE_PAINEL)?.cards).toMatchObject([
      { clienteNome: "Maria Souza", estagio: "NOVO_CONTATO" },
    ]);
    expect(await screen.findByText("Contato de Maria Souza registrado.")).toBeInTheDocument();
  });

  it("erro da API com campo aparece embaixo do campo", async () => {
    const api = apiDeMemoria(novoCrm());
    api.clientes.registrarContato = () =>
      Promise.reject(new ErroRemoto(422, "FormatoInvalido", "E-mail recusado pelo servidor.", "email"));
    renderComApi(<FormNovoContato />, api);

    await preencher({ Nome: "Maria", Telefone: "31998765432", "E-mail": "maria@abc.com.br" });

    expect(await screen.findByLabelText(/^E-mail/)).toHaveAccessibleDescription(
      "E-mail recusado pelo servidor.",
    );
    expect(push).not.toHaveBeenCalled();
  });

  it("erro sem campo aparece como alerta geral", async () => {
    const api = apiDeMemoria(novoCrm());
    api.clientes.registrarContato = () => Promise.reject(new Error("boom"));
    renderComApi(<FormNovoContato />, api);

    await preencher({ Nome: "Maria", Telefone: "31998765432", "E-mail": "maria@abc.com.br" });

    expect(await screen.findByRole("alert")).toHaveTextContent("Algo deu errado. Tente de novo.");
  });
});
