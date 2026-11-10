import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ConsultarCliente } from "@/application/use-cases/consultar-cliente";
import { FichaCliente } from "@/components/clientes/ficha-cliente";
import { Email } from "@/domain/value-objects/email";
import { Telefone } from "@/domain/value-objects/telefone";
import { CrmEmMemoria } from "@/infra/memoria/crm-em-memoria";

import { MAPA_DA_API } from "../unit/domain/fixtures";

let agora = new Date("2026-09-15T15:00:00Z");

async function clienteComHistorico() {
  agora = new Date("2026-09-15T15:00:00Z");
  const crm = new CrmEmMemoria(MAPA_DA_API, () => agora);
  const { clienteId, orcamento } = await crm.clientes.registrarContato({
    nome: "Maria Souza",
    telefone: Telefone.criar("31998765432"),
    email: Email.criar("maria@abc.com.br"),
    empresa: "Embalagens ABC",
    tipoEmbalagemInteresse: "Caixa de papelão",
  });
  return { crm, clienteId, orcamentoId: orcamento.id };
}

describe("Ficha do cliente (RF07, RF08)", () => {
  it("mostra os dados de contato formatados e os orçamentos", async () => {
    const { crm, clienteId } = await clienteComHistorico();

    render(<FichaCliente detalhe={await new ConsultarCliente(crm.clientes).executar(clienteId)} />);

    expect(screen.getByRole("heading", { level: 1, name: "Maria Souza" })).toBeInTheDocument();
    expect(screen.getByText("(31) 99876-5432")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "maria@abc.com.br" })).toHaveAttribute(
      "href",
      "mailto:maria@abc.com.br",
    );
    expect(screen.getByText("Embalagens ABC")).toBeInTheDocument();
    expect(screen.getByText("Caixa de papelão")).toBeInTheDocument();
    const orcamentos = screen.getByRole("region", { name: "Orçamentos" });
    expect(within(orcamentos).getByText("Novo contato")).toBeInTheDocument();
    expect(within(orcamentos).getByText("Sem valor")).toBeInTheDocument();
    expect(screen.getByText("Nenhuma interação registrada ainda.")).toBeInTheDocument();
  });

  it("linha do tempo com a interação mais recente primeiro", async () => {
    const { crm, clienteId, orcamentoId } = await clienteComHistorico();
    await crm.orcamentos.registrarInteracao(orcamentoId, "LIGACAO", "Primeiro retorno");
    agora = new Date("2026-09-16T13:30:00Z");
    await crm.orcamentos.registrarInteracao(orcamentoId, "REUNIAO", "Visita na fábrica");

    render(<FichaCliente detalhe={await new ConsultarCliente(crm.clientes).executar(clienteId)} />);

    const itens = within(screen.getByRole("list", { name: "Linha do tempo" })).getAllByRole("listitem");
    expect(itens.map((i) => i.textContent)).toEqual([
      expect.stringMatching(/Reunião.*16\/09\/2026.*10:30.*Visita na fábrica/),
      expect.stringMatching(/Ligação.*15\/09\/2026.*Primeiro retorno/),
    ]);
    expect(screen.getByText("1 orçamento · 2 interações")).toBeInTheDocument();
  });
});
