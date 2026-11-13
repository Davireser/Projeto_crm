import type { ClienteGateway } from "@/application/ports";
import type { Orcamento } from "@/domain/entities/orcamento";
import { OperacaoNaoPermitida } from "@/domain/errors";

/** Cliente perdido volta ao funil com um novo orçamento em Novo contato. */
export class ReabrirAtendimento {
  constructor(private readonly clientes: ClienteGateway) {}

  async executar(perdido: Orcamento): Promise<Orcamento> {
    if (!perdido.podeReabrirAtendimento()) {
      throw new OperacaoNaoPermitida("Só dá para reabrir o atendimento a partir de um orçamento perdido.", "estagio");
    }
    return this.clientes.reabrirAtendimento(perdido.clienteId, perdido.clienteNome);
  }
}
