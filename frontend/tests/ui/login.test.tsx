import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { FormLogin } from "@/components/sessao/form-login";
import type { EstadoLogin } from "@/lib/sessao/estado-login";

describe("FormLogin", () => {
  it("envia e-mail, senha e o destino para a ação", async () => {
    const acao = vi.fn(async (_estado: EstadoLogin, _form: FormData): Promise<EstadoLogin> => ({
      erro: null,
      email: "",
    }));
    render(<FormLogin acao={acao} de="/metricas" />);

    await userEvent.type(screen.getByLabelText("E-mail"), "davi@x.com");
    await userEvent.type(screen.getByLabelText("Senha"), "segredo");
    await userEvent.click(screen.getByRole("button", { name: "Entrar" }));

    expect(acao).toHaveBeenCalledOnce();
    const form = acao.mock.calls[0]![1];
    expect(Object.fromEntries(form)).toEqual({ email: "davi@x.com", senha: "segredo", de: "/metricas" });
  });

  it("mostra o erro devolvido e mantém o e-mail digitado", async () => {
    const acao = vi.fn(async (): Promise<EstadoLogin> => ({
      erro: "E-mail ou senha incorretos.",
      email: "davi@x.com",
    }));
    render(<FormLogin acao={acao} de={null} />);

    await userEvent.type(screen.getByLabelText("E-mail"), "davi@x.com");
    await userEvent.type(screen.getByLabelText("Senha"), "errada");
    await userEvent.click(screen.getByRole("button", { name: "Entrar" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("E-mail ou senha incorretos.");
    expect(screen.getByLabelText("E-mail")).toHaveValue("davi@x.com");
    expect(screen.getByLabelText("Senha")).toHaveValue("");
  });

  it("desabilita o botão enquanto envia", async () => {
    let liberar: () => void = () => {};
    const acao = vi.fn(
      () => new Promise<EstadoLogin>((resolve) => {
        liberar = () => resolve({ erro: null, email: "" });
      }),
    );
    render(<FormLogin acao={acao} de={null} />);

    await userEvent.type(screen.getByLabelText("E-mail"), "davi@x.com");
    await userEvent.type(screen.getByLabelText("Senha"), "x");
    await userEvent.click(screen.getByRole("button", { name: "Entrar" }));

    expect(await screen.findByRole("button", { name: "Entrando…" })).toBeDisabled();
    liberar();
  });
});
