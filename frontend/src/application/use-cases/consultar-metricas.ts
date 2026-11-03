import type { MetricasGateway } from "@/application/ports";
import type { MetricasFunil } from "@/domain/entities/metricas-funil";

/** UC08: indicadores do funil (RF06). */
export class ConsultarMetricas {
  constructor(private readonly metricas: MetricasGateway) {}

  executar(): Promise<MetricasFunil> {
    return this.metricas.obter();
  }
}
