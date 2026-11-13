"use client";

import type { ReactNode } from "react";

import { COR_DO_ESTAGIO } from "@/components/estagio/cor-do-estagio";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import type {
  DadosMetricasFunil,
  MetricasFunil,
  TotalDoEstagio,
} from "@/domain/entities/metricas-funil";
import { rotuloDoEstagio } from "@/domain/value-objects/estagio-atendimento";
import { formatarCentavos } from "@/domain/value-objects/valor-orcado";
import { useMetricas } from "@/hooks/use-metricas";
import { mensagemDeErro } from "@/lib/mensagens";

const plural = (n: number, singular: string, plural: string) =>
  `${n} ${n === 1 ? singular : plural}`;

/** Indicadores do funil (RF06): a taxa de fechamento em destaque, as contagens e o dinheiro por etapa. */
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
    <div className="grid gap-4">
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
          <Indicador
            nome="Em aberto"
            valor={metricas.emAberto}
            nota="No funil agora."
          />
          <Indicador
            nome="Fechados"
            valor={metricas.fechados}
            nota="Viraram venda."
          />
          <Indicador
            nome="Perdidos"
            valor={metricas.perdidos}
            nota="Encerrados sem venda."
          />
        </div>
      </div>
      <DinheiroPorEtapa metricas={metricas} />
    </div>
  );
}

/** Soma dos valores em cada estágio, com barras na mesma escala para comparar de relance. */
function DinheiroPorEtapa({ metricas }: { metricas: MetricasFunil }) {
  const maior = metricas.maiorValorDeEstagio();
  const semValorEmAberto = metricas.porEstagio
    .filter((t) => t.estagio !== "FECHADO" && t.estagio !== "PERDIDO")
    .reduce((soma, t) => soma + t.semValor, 0);

  return (
    <div className="grid gap-4 md:grid-cols-[minmax(0,1.4fr)_minmax(0,2fr)]">
      <Indicador
        nome="Em jogo no funil"
        valor={formatarCentavos(metricas.valorEmAberto())}
        nota={
          semValorEmAberto === 0
            ? "Soma dos orçamentos em aberto."
            : `Soma dos orçamentos em aberto; ${plural(semValorEmAberto, "ainda está sem valor", "ainda estão sem valor")}.`
        }
      />
      <Card className="gap-0 py-0">
        <CardContent className="grid gap-4 p-5">
          <h2
            id="dinheiro-por-etapa"
            className="text-sm font-medium text-muted-foreground"
          >
            Dinheiro por etapa
          </h2>
          <ul aria-labelledby="dinheiro-por-etapa" className="grid gap-4">
            {metricas.porEstagio.map((total) => (
              <LinhaDaEtapa key={total.estagio} total={total} maior={maior} />
            ))}
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}

function LinhaDaEtapa({
  total,
  maior,
}: {
  total: TotalDoEstagio;
  maior: number;
}) {
  const id = `etapa-${total.estagio.toLowerCase()}`;
  const largura = maior > 0 ? (100 * total.valorCentavos) / maior : 0;
  const detalhes = [plural(total.quantidade, "orçamento", "orçamentos")];
  if (total.semValor > 0) detalhes.push(`${total.semValor} sem valor`);

  return (
    <li aria-labelledby={id} className="grid gap-1.5">
      <div className="flex items-baseline justify-between gap-3">
        <span className="flex items-center gap-2 text-sm font-medium">
          <span
            className={`size-2 rounded-full ${COR_DO_ESTAGIO[total.estagio]}`}
            aria-hidden
          />
          <span id={id}>{rotuloDoEstagio(total.estagio)}</span>
        </span>
        <span className="text-sm font-semibold tabular-nums">
          {formatarCentavos(total.valorCentavos)}
        </span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-muted" aria-hidden>
        <div
          className={`h-full rounded-full ${COR_DO_ESTAGIO[total.estagio]}`}
          style={{ width: `${largura}%` }}
        />
      </div>
      <p className="text-xs text-muted-foreground">{detalhes.join(" · ")}</p>
    </li>
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
        <p
          className={
            destaque
              ? "text-5xl font-semibold tracking-tight tabular-nums"
              : "text-3xl font-semibold tabular-nums"
          }
        >
          {valor}
        </p>
        <p className="text-xs text-muted-foreground">{nota}</p>
      </CardContent>
    </Card>
  );
}

export function EsqueletoMetricas() {
  return (
    <div
      className="grid gap-4"
      aria-busy="true"
      aria-label="Carregando métricas"
    >
      <div className="grid gap-4 md:grid-cols-[minmax(0,1.4fr)_minmax(0,2fr)]">
        <Skeleton className="h-40" />
        <div className="grid gap-4 sm:grid-cols-3">
          <Skeleton className="h-40" />
          <Skeleton className="h-40" />
          <Skeleton className="h-40" />
        </div>
      </div>
      <div className="grid gap-4 md:grid-cols-[minmax(0,1.4fr)_minmax(0,2fr)]">
        <Skeleton className="h-40" />
        <Skeleton className="h-72" />
      </div>
    </div>
  );
}
