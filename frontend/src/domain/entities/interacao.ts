import { FormatoInvalido } from "@/domain/errors";
import type { TipoInteracao } from "@/domain/value-objects/tipo-interacao";

export interface DadosInteracao {
  id: string;
  tipo: TipoInteracao;
  conteudo: string;
  /** Data e hora ISO 8601 em UTC, definida pelo servidor. */
  dataHora: string;
}

/** Registro imutável de um contato feito com o cliente (RF04). */
export class Interacao implements DadosInteracao {
  readonly id: string;
  readonly tipo: TipoInteracao;
  readonly conteudo: string;
  readonly dataHora: string;

  constructor(dados: DadosInteracao) {
    this.id = dados.id;
    this.tipo = dados.tipo;
    this.conteudo = dados.conteudo;
    this.dataHora = dados.dataHora;
    Object.freeze(this);
  }

  static validarConteudo(conteudo: string): string {
    const limpo = conteudo.trim();
    if (!limpo) {
      throw new FormatoInvalido("O conteúdo da interação é obrigatório.", "conteudo");
    }
    return limpo;
  }
}
