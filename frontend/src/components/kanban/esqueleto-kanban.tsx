import { Skeleton } from "@/components/ui/skeleton";
import { ESTAGIOS } from "@/domain/value-objects/estagio-atendimento";

/** Placeholder do painel enquanto os dados chegam (faz parte do shell estático). */
export function EsqueletoKanban() {
  return (
    <div className="grid gap-4" aria-busy="true" aria-label="Carregando o painel">
      <Skeleton className="h-9 w-64" />
      <div className="grid auto-cols-[minmax(15rem,1fr)] grid-flow-col gap-4 overflow-hidden">
        {ESTAGIOS.map((estagio) => (
          <div key={estagio} className="grid content-start gap-2 rounded-xl border bg-muted/40 p-3">
            <Skeleton className="h-4 w-28" />
            <Skeleton className="h-20 w-full" />
            <Skeleton className="h-20 w-full" />
          </div>
        ))}
      </div>
    </div>
  );
}
