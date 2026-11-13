import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { BotaoSair } from "@/components/sessao/botao-sair";
import { DropdownMenu, DropdownMenuContent, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { CHAVE_DO_CACHE } from "@/lib/query/provedor-query";

describe("BotaoSair", () => {
  it("apaga o cache offline e chama a ação de sair", async () => {
    const queryClient = new QueryClient();
    queryClient.setQueryData(["painel"], { cards: 3 });
    window.localStorage.setItem(CHAVE_DO_CACHE, "dados do usuário anterior");
    const sair = vi.fn(async () => {});

    render(
      <QueryClientProvider client={queryClient}>
        <DropdownMenu>
          <DropdownMenuTrigger>Conta</DropdownMenuTrigger>
          <DropdownMenuContent>
            <BotaoSair sair={sair} />
          </DropdownMenuContent>
        </DropdownMenu>
      </QueryClientProvider>,
    );
    await userEvent.click(screen.getByText("Conta"));
    await userEvent.click(await screen.findByRole("menuitem", { name: "Sair" }));

    await vi.waitFor(() => expect(sair).toHaveBeenCalledOnce());
    expect(window.localStorage.getItem(CHAVE_DO_CACHE)).toBeNull();
    expect(queryClient.getQueryData(["painel"])).toBeUndefined();
  });
});
