import type { Estagio } from "@/domain/value-objects/estagio-atendimento";

/** Quanto dinheiro está num estágio do funil. Orçamentos sem valor ficam fora da soma. */
export interface TotalDoEstagio {
  estagio: Estagio;
  quantidade: number;
  valorCentavos: number;
  semValor: number;
}

export interface DadosMetricasFunil {
  emAberto: number;
  fechados: number;
  perdidos: number;
  /** Percentual de fechados sobre concluídos; `null` quando nada foi concluído (RN07). */
  taxaFechamento: number | null;
  /** Um item por estágio, na ordem do funil. */
  porEstagio: TotalDoEstagio[];
}

const PERCENTUAL = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 2 });
const CONCLUIDOS: readonly Estagio[] = ["FECHADO", "PERDIDO"];

/** Indicadores do funil (RF06). */
export class MetricasFunil implements DadosMetricasFunil {
  readonly emAberto: number;
  readonly fechados: number;
  readonly perdidos: number;
  readonly taxaFechamento: number | null;
  readonly porEstagio: TotalDoEstagio[];

  constructor(dados: DadosMetricasFunil) {
    this.emAberto = dados.emAberto;
    this.fechados = dados.fechados;
    this.perdidos = dados.perdidos;
    this.taxaFechamento = dados.taxaFechamento;
    // `?? []`: cache offline gravado por uma versão anterior, sem esse campo.
    this.porEstagio = dados.porEstagio ?? [];
    Object.freeze(this);
  }

  /** `62,5%`, ou `—` quando ainda não há orçamento concluído (não zero, RN07). */
  taxaFormatada(): string {
    return this.taxaFechamento === null ? "—" : `${PERCENTUAL.format(this.taxaFechamento)}%`;
  }

  /** Centavos ainda em jogo: soma dos estágios que não foram concluídos. */
  valorEmAberto(): number {
    return this.porEstagio
      .filter((t) => !CONCLUIDOS.includes(t.estagio))
      .reduce((soma, t) => soma + t.valorCentavos, 0);
  }

  /** Maior soma entre os estágios: a escala das barras. */
  maiorValorDeEstagio(): number {
    return Math.max(0, ...this.porEstagio.map((t) => t.valorCentavos));
  }
}
