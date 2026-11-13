"use client";

import type { ReactNode } from "react";

import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import type { DadosMetricasFunil } from "@/domain/entities/metricas-funil";
import { useMetricas } from "@/hooks/use-metricas";
import { mensagemDeErro } from "@/lib/mensagens";

const plural = (n: number, singular: string, plural: string) => `${n} ${n === 1 ? singular : plural}`;

/** Indicadores do funil (RF06): a taxa de fechamento em destaque e as contagens ao lado. */
export function PainelMetricas({ inicial }: { inicial?: DadosMetricasFunil }) {
  const { data: metricas, error } = useMetricas(inicial);

  if (!metricas) {
    if (error) {
      return (
        <p role="alert" className="text-destructive">
          Não foi possível carregar as métricas. {mensagemDeErro(error)}
        </p>
      );
    }
    return <EsqueletoMetricas />;
  }

  const concluidos = metricas.fechados + metricas.perdidos;

  return (
    <div className="grid gap-4 md:grid-cols-[minmax(0,1.4fr)_minmax(0,2fr)]">
      <Indicador
        nome="Taxa de fechamento"
        valor={metricas.taxaFormatada()}
        destaque
        nota={
          concluidos === 0
            ? "Nenhum orçamento concluído ainda."
            : `${metricas.fechados} de ${plural(concluidos, "concluído", "concluídos")} (fechados ÷ fechados + perdidos).`
        }
      />
      <div className="grid gap-4 sm:grid-cols-3">
        <Indicador nome="Em aberto" valor={metricas.emAberto} nota="No funil agora." />
        <Indicador nome="Fechados" valor={metricas.fechados} nota="Viraram venda." />
        <Indicador nome="Perdidos" valor={metricas.perdidos} nota="Encerrados sem venda." />
      </div>
    </div>
  );
}

interface PropsIndicador {
  nome: string;
  valor: ReactNode;
  nota: string;
  destaque?: boolean;
}

function Indicador({ nome, valor, nota, destaque = false }: PropsIndicador) {
  const id = `indicador-${nome.toLowerCase().replace(/\s+/g, "-")}`;
  return (
    <Card role="group" aria-labelledby={id} className="gap-0 py-0">
      <CardContent className="grid content-between gap-3 p-5">
        <h2 id={id} className="text-sm font-medium text-muted-foreground">
          {nome}
        </h2>
        <p className={destaque ? "text-5xl font-semibold tracking-tight tabular-nums" : "text-3xl font-semibold tabular-nums"}>
          {valor}
        </p>
        <p className="text-xs text-muted-foreground">{nota}</p>
      </CardContent>
    </Card>
  );
}

export function EsqueletoMetricas() {
  return (
    <div className="grid gap-4 md:grid-cols-[minmax(0,1.4fr)_minmax(0,2fr)]" aria-busy="true" aria-label="Carregando métricas">
      <Skeleton className="h-40" />
      <div className="grid gap-4 sm:grid-cols-3">
        <Skeleton className="h-40" />
        <Skeleton className="h-40" />
        <Skeleton className="h-40" />
      </div>
    </div>
  );
}
