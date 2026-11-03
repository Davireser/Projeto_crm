import type { ClienteGateway, ItemHistorico } from "@/application/ports";
import type { Cliente } from "@/domain/entities/cliente";
import { Orcamento } from "@/domain/entities/orcamento";

export interface DetalheCliente {
  cliente: Cliente;
  orcamentos: Orcamento[];
  historico: ItemHistorico[];
}

/** UC07: cliente, seus orçamentos (RF08) e a linha do tempo de interações (RF07). */
export class ConsultarCliente {
  constructor(private readonly clientes: ClienteGateway) {}

  async executar(id: string): Promise<DetalheCliente> {
    const [{ cliente, orcamentos }, historico] = await Promise.all([
      this.clientes.obterCliente(id),
      this.clientes.historico(id),
    ]);
    const porOrcamento = new Map<string, number>();
    for (const item of historico) {
      porOrcamento.set(item.orcamentoId, (porOrcamento.get(item.orcamentoId) ?? 0) + 1);
    }
    return {
      cliente,
      orcamentos: orcamentos.map(
        (o) => new Orcamento({ ...o, qtdInteracoes: porOrcamento.get(o.id) ?? 0 }),
      ),
      historico,
    };
  }
}
