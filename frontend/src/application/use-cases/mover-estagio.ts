import type { OrcamentoGateway } from "@/application/ports";
import { Orcamento } from "@/domain/entities/orcamento";
import type { Funil } from "@/domain/funil/funil";
import type { Estagio } from "@/domain/value-objects/estagio-atendimento";

/**
 * UC03: o domínio valida antes (transição inválida nem chega na API) e o
 * backend confirma. O resultado combina o card local com a resposta da API.
 */
export class MoverEstagio {
  constructor(private readonly orcamentos: OrcamentoGateway) {}

  async executar(orcamento: Orcamento, destino: Estagio, funil: Funil): Promise<Orcamento> {
    orcamento.validarMovimento(destino, funil);
    const confirmado = await this.orcamentos.moverEstagio(orcamento.id, destino);
    return new Orcamento({ ...orcamento, ...confirmado });
  }
}
