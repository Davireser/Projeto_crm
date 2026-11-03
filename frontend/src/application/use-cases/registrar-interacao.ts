import type { OrcamentoGateway } from "@/application/ports";
import { Interacao } from "@/domain/entities/interacao";
import type { TipoInteracao } from "@/domain/value-objects/tipo-interacao";

/** UC06: registra a interação; a data e hora são definidas pelo servidor (RF04). */
export class RegistrarInteracao {
  constructor(private readonly orcamentos: OrcamentoGateway) {}

  async executar(orcamentoId: string, tipo: TipoInteracao, conteudo: string): Promise<Interacao> {
    return this.orcamentos.registrarInteracao(orcamentoId, tipo, Interacao.validarConteudo(conteudo));
  }
}
