import type { Estagio } from "@/domain/value-objects/estagio-atendimento";

/** Cor de cada estágio, a mesma no Kanban e nas métricas. */
export const COR_DO_ESTAGIO: Record<Estagio, string> = {
  NOVO_CONTATO: "bg-sky-500",
  EM_NEGOCIACAO: "bg-amber-500",
  ORCAMENTO_ENVIADO: "bg-violet-500",
  FECHADO: "bg-emerald-500",
  PERDIDO: "bg-rose-500",
};
