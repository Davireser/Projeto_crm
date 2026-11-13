/**
 * Painel Kanban (RF02, RF03, RF04, RF05, RNF02).
 *
 * O arraste e os botões "Mover para" chamam a mesma função (`useTentarMover`),
 * então a atualização otimista e o rollback são testados pelos botões: o jsdom
 * não calcula posição dos elementos, que o dnd-kit precisa para o arraste.
 */
import { screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ErroRemoto } from "@/application/errors";
import { RegistrarContato } from "@/application/use-cases/registrar-contato";
import { Kanban } from "@/components/kanban/kanban";
import { CrmEmMemoria } from "@/infra/memoria/crm-em-memoria";
import { ValorOrcado } from "@/domain/value-objects/valor-orcado";

import { apiDeMemoria, novoCrm, renderComApi } from "./apoio";

let crm: CrmEmMemoria;

beforeEach(async () => {
  crm = novoCrm();
  const registrar = new RegistrarContato(crm.clientes);
  const { orcamento: deMaria } = await registrar.executar({ nome: "Maria", telefone: "31998765432", email: "maria@x.com" });
  const { orcamento: deJoao } = await registrar.executar({ nome: "João", telefone: "31998765433", email: "joao@x.com" });
  await crm.orcamentos.definirValor(deJoao.id, ValorOrcado.deTexto("4200"));
  await crm.orcamentos.moverEstagio(deJoao.id, "EM_NEGOCIACAO");
  void deMaria;
});

// `hidden: true`: com a gaveta (modal) aberta, o fundo fica aria-hidden para leitores de tela.
const coluna = (nome: string) =>
  screen.getByRole("region", { name: new RegExp(`^${nome}, \\d`), hidden: true });

async function renderizarPainel(api = apiDeMemoria(crm)) {
  const resultado = renderComApi(<Kanban />, api);
  await screen.findByRole("region", { name: /^Novo contato, \d/ });
  return resultado;
}

async function abrirCard(nome: string) {
  await userEvent.click(screen.getByRole("button", { name: `Abrir orçamento de ${nome}` }));
  return screen.findByRole("dialog");
}

describe("Kanban", () => {
  it("mostra as cinco colunas com os cards no estágio certo", async () => {
    await renderizarPainel();

    expect(screen.getAllByRole("region", { name: /, \d+ orçamentos?$/ })).toHaveLength(5);
    expect(within(coluna("Novo contato")).getByText("Maria")).toBeInTheDocument();
    expect(within(coluna("Em negociação")).getByText("João")).toBeInTheDocument();
    expect(within(coluna("Em negociação")).getByText(/^R\$\s4\.200,00$/)).toBeInTheDocument();
    expect(coluna("Fechado")).toHaveAccessibleName("Fechado, 0 orçamentos");
  });

  it("move o card para outra coluna e confirma na API", async () => {
    await renderizarPainel();

    const gaveta = await abrirCard("Maria");
    await userEvent.click(within(gaveta).getByRole("button", { name: "Mover para Em negociação" }));

    expect(await within(coluna("Em negociação")).findByText("Maria")).toBeInTheDocument();
    expect(crm.orcamentos.chamadas).toContainEqual(expect.stringMatching(/^mover orc-\d+ EM_NEGOCIACAO$/));
  });

  it("desfaz o movimento e mostra o motivo quando a API recusa (rollback)", async () => {
    const api = apiDeMemoria(crm);
    let recusar: (erro: unknown) => void = () => {};
    const real = crm.orcamentos;
    api.orcamentos = {
      listarCards: () => real.listarCards(),
      obterTransicoes: () => real.obterTransicoes(),
      definirValor: (id, valor) => real.definirValor(id, valor),
      registrarInteracao: (id, tipo, conteudo) => real.registrarInteracao(id, tipo, conteudo),
      moverEstagio: vi.fn(() => new Promise<never>((_ok, falhar) => (recusar = falhar))),
    };
    await renderizarPainel(api);

    const gaveta = await abrirCard("Maria");
    await userEvent.click(within(gaveta).getByRole("button", { name: "Mover para Em negociação" }));

    // Otimista: o card muda de coluna antes da resposta.
    expect(await within(coluna("Em negociação")).findByText("Maria")).toBeInTheDocument();

    recusar(new ErroRemoto(422, "TransicaoInvalida", "O servidor recusou a mudança."));

    expect(await screen.findByText("O servidor recusou a mudança.")).toBeInTheDocument();
    expect(await within(coluna("Novo contato")).findByText("Maria")).toBeInTheDocument();
    expect(within(coluna("Em negociação")).queryByText("Maria")).not.toBeInTheDocument();
  });

  it("só oferece os destinos que o funil permite (RN01)", async () => {
    await renderizarPainel();

    const gaveta = await abrirCard("Maria");

    expect(
      within(gaveta)
        .getAllByRole("button", { name: /^Mover para/ })
        .map((b) => b.textContent),
    ).toEqual(["Em negociação", "Perdido"]);
  });

  it("orçamento sem valor não vai para Orçamento enviado (RN02)", async () => {
    await renderizarPainel();
    const gaveta = await abrirCard("Maria");
    await userEvent.click(within(gaveta).getByRole("button", { name: "Mover para Em negociação" }));
    await within(coluna("Em negociação")).findByText("Maria");
    const chamadasAntes = crm.orcamentos.chamadas.length;

    await userEvent.click(within(gaveta).getByRole("button", { name: "Mover para Orçamento enviado" }));

    expect(await screen.findByText(/Defina o valor do orçamento antes/)).toBeInTheDocument();
    expect(crm.orcamentos.chamadas).toHaveLength(chamadasAntes);
  });

  it("define o valor pela gaveta", async () => {
    await renderizarPainel();
    const gaveta = await abrirCard("Maria");

    await userEvent.type(within(gaveta).getByLabelText("Valor (R$)"), "1.500,50");
    await userEvent.click(within(gaveta).getByRole("button", { name: "Salvar valor" }));

    expect(await within(coluna("Novo contato")).findByText(/^R\$\s1\.500,50$/)).toBeInTheDocument();
  });

  it("valor inválido aparece no formulário", async () => {
    await renderizarPainel();
    const gaveta = await abrirCard("Maria");

    await userEvent.type(within(gaveta).getByLabelText("Valor (R$)"), "abc");
    await userEvent.click(within(gaveta).getByRole("button", { name: "Salvar valor" }));

    expect(await within(gaveta).findByText(/Valor orçado inválido/)).toBeInTheDocument();
  });

  it("registra uma interação e atualiza a contagem do card", async () => {
    await renderizarPainel();
    const gaveta = await abrirCard("Maria");

    await userEvent.click(within(gaveta).getByRole("radio", { name: "Ligação" }));
    await userEvent.type(within(gaveta).getByLabelText("O que foi conversado"), "Pediu 500 caixas");
    await userEvent.click(within(gaveta).getByRole("button", { name: "Registrar interação" }));

    expect(await screen.findByText("Interação registrada.")).toBeInTheDocument();
    expect(within(coluna("Novo contato")).getByLabelText("1 interação")).toBeInTheDocument();
    expect(within(gaveta).getByLabelText("O que foi conversado")).toHaveValue("");
  });

  it("filtra os cards pelo nome do cliente", async () => {
    await renderizarPainel();

    await userEvent.type(screen.getByRole("searchbox", { name: "Buscar cliente" }), "joa");

    expect(screen.queryByText("Maria")).not.toBeInTheDocument();
    expect(screen.getByText("João")).toBeInTheDocument();
  });

  it("estágio terminal não oferece movimentos nem edição de valor", async () => {
    await crm.orcamentos.moverEstagio((await crm.orcamentos.listarCards())[0]!.id, "PERDIDO");
    await renderizarPainel();

    const gaveta = await abrirCard("Maria");

    expect(within(gaveta).getByText("Orçamento encerrado.")).toBeInTheDocument();
    expect(within(gaveta).queryByLabelText("Valor (R$)")).not.toBeInTheDocument();
    expect(within(gaveta).getByRole("button", { name: "Reabrir atendimento" })).toBeInTheDocument();
  });

  it("cliente perdido volta ao funil com um novo orçamento", async () => {
    await crm.orcamentos.moverEstagio((await crm.orcamentos.listarCards())[0]!.id, "PERDIDO");
    await renderizarPainel();
    const gaveta = await abrirCard("Maria");

    await userEvent.click(within(gaveta).getByRole("button", { name: "Reabrir atendimento" }));

    expect(await screen.findByText("Atendimento de Maria reaberto em Novo contato.")).toBeInTheDocument();
    expect(within(coluna("Novo contato")).getByText("Maria")).toBeInTheDocument();
    expect(within(coluna("Perdido")).getByText("Maria")).toBeInTheDocument();
    // A gaveta passa a mostrar o orçamento novo, já com os movimentos liberados.
    expect(within(screen.getByRole("dialog")).getByRole("button", { name: "Mover para Em negociação" })).toBeInTheDocument();
  });

  it("não reabre quem já tem orçamento em aberto: o motivo aparece num aviso", async () => {
    const [deMaria] = await crm.orcamentos.listarCards();
    await crm.orcamentos.moverEstagio(deMaria!.id, "PERDIDO");
    await crm.clientes.reabrirAtendimento(deMaria!.clienteId, "Maria");
    await renderizarPainel();
    await userEvent.click(within(coluna("Perdido")).getByRole("button", { name: "Abrir orçamento de Maria" }));

    await userEvent.click(within(await screen.findByRole("dialog")).getByRole("button", { name: "Reabrir atendimento" }));

    expect(await screen.findByText("Maria já tem um orçamento em aberto.")).toBeInTheDocument();
  });
});
