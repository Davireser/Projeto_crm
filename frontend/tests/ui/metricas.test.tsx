import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { RegistrarContato } from "@/application/use-cases/registrar-contato";
import { PainelMetricas } from "@/components/metricas/painel-metricas";
import { ValorOrcado } from "@/domain/value-objects/valor-orcado";

import { apiDeMemoria, novoCrm, renderComApi } from "./apoio";

const indicador = (nome: string) => screen.getByRole("group", { name: nome });

describe("Métricas do funil (RF06, RN07)", () => {
  it("sem orçamento concluído, a taxa aparece como — (não zero)", async () => {
    const crm = novoCrm();
    await new RegistrarContato(crm.clientes).executar({ nome: "Maria", telefone: "31998765432", email: "m@x.com" });

    renderComApi(<PainelMetricas />, apiDeMemoria(crm));

    expect(await screen.findByRole("group", { name: "Em aberto" })).toHaveTextContent("1");
    expect(indicador("Taxa de fechamento")).toHaveTextContent("—");
    expect(indicador("Taxa de fechamento")).toHaveTextContent("Nenhum orçamento concluído ainda");
  });

  it("taxa = fechados ÷ (fechados + perdidos)", async () => {
    const crm = novoCrm();
    const registrar = new RegistrarContato(crm.clientes);
    for (const [i, destino] of (["FECHADO", "FECHADO", "PERDIDO", null] as const).entries()) {
      const { orcamento } = await registrar.executar({ nome: `C${i}`, telefone: "31998765432", email: `c${i}@x.com` });
      if (!destino) continue;
      await crm.orcamentos.definirValor(orcamento.id, ValorOrcado.deTexto("100"));
      if (destino === "PERDIDO") {
        await crm.orcamentos.moverEstagio(orcamento.id, "PERDIDO");
        continue;
      }
      for (const e of ["EM_NEGOCIACAO", "ORCAMENTO_ENVIADO", "FECHADO"] as const) {
        await crm.orcamentos.moverEstagio(orcamento.id, e);
      }
    }

    renderComApi(<PainelMetricas />, apiDeMemoria(crm));

    expect(await screen.findByRole("group", { name: "Taxa de fechamento" })).toHaveTextContent("66,67%");
    expect(indicador("Taxa de fechamento")).toHaveTextContent("2 de 3 concluídos");
    expect(indicador("Fechados")).toHaveTextContent("2");
    expect(indicador("Perdidos")).toHaveTextContent("1");
    expect(indicador("Em aberto")).toHaveTextContent("1");
  });

  it("usa os dados que vieram do servidor na primeira pintura", () => {
    renderComApi(
      <PainelMetricas inicial={{ emAberto: 7, fechados: 5, perdidos: 3, taxaFechamento: 62.5 }} />,
      apiDeMemoria(novoCrm()),
    );

    expect(indicador("Em aberto")).toHaveTextContent("7");
    expect(indicador("Taxa de fechamento")).toHaveTextContent("62,5%");
  });
});
