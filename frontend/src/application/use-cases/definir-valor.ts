import type { OrcamentoGateway } from "@/application/ports";
import { Orcamento } from "@/domain/entities/orcamento";
import type { Funil } from "@/domain/funil/funil";
import { ValorOrcado } from "@/domain/value-objects/valor-orcado";

/** UC05: lê o valor digitado, valida no domínio e grava na API (RF03). */
export class DefinirValor {
  constructor(private readonly orcamentos: OrcamentoGateway) {}

  async executar(orcamento: Orcamento, texto: string, funil: Funil): Promise<Orcamento> {
    const valor = ValorOrcado.deTexto(texto);
    orcamento.definirValor(valor, funil); // valida: orçamento encerrado não muda de valor
    const confirmado = await this.orcamentos.definirValor(orcamento.id, valor);
    return new Orcamento({ ...orcamento, ...confirmado });
  }
}
