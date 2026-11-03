export interface DadosMetricasFunil {
  emAberto: number;
  fechados: number;
  perdidos: number;
  /** Percentual de fechados sobre concluídos; `null` quando nada foi concluído (RN07). */
  taxaFechamento: number | null;
}

const PERCENTUAL = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 2 });

/** Indicadores do funil (RF06). */
export class MetricasFunil implements DadosMetricasFunil {
  readonly emAberto: number;
  readonly fechados: number;
  readonly perdidos: number;
  readonly taxaFechamento: number | null;

  constructor(dados: DadosMetricasFunil) {
    this.emAberto = dados.emAberto;
    this.fechados = dados.fechados;
    this.perdidos = dados.perdidos;
    this.taxaFechamento = dados.taxaFechamento;
    Object.freeze(this);
  }

  /** `62,5%`, ou `—` quando ainda não há orçamento concluído (não zero, RN07). */
  taxaFormatada(): string {
    return this.taxaFechamento === null ? "—" : `${PERCENTUAL.format(this.taxaFechamento)}%`;
  }
}
