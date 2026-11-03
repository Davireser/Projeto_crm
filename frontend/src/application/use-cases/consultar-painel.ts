import type { OrcamentoGateway } from "@/application/ports";
import type { Orcamento } from "@/domain/entities/orcamento";
import { Funil } from "@/domain/funil/funil";
import { ESTAGIOS, type Estagio } from "@/domain/value-objects/estagio-atendimento";

export type Colunas = Record<Estagio, Orcamento[]>;

export interface Painel {
  funil: Funil;
  colunas: Colunas;
}

/** Distribui os cards nas cinco colunas do Kanban, mantendo a ordem recebida. */
export function montarColunas(cards: readonly Orcamento[]): Colunas {
  const colunas = Object.fromEntries(ESTAGIOS.map((e) => [e, [] as Orcamento[]])) as Colunas;
  for (const card of cards) colunas[card.estagio].push(card);
  return colunas;
}

/** UC: carregar o painel Kanban (RF05) com as regras do funil vindas da API. */
export class ConsultarPainel {
  constructor(private readonly orcamentos: OrcamentoGateway) {}

  async executar(): Promise<Painel> {
    const [cards, mapa] = await Promise.all([
      this.orcamentos.listarCards(),
      this.orcamentos.obterTransicoes(),
    ]);
    return { funil: Funil.doMapa(mapa), colunas: montarColunas(cards) };
  }
}
