"use client";

import { useDroppable } from "@dnd-kit/core";

import { COR_DO_ESTAGIO } from "@/components/estagio/cor-do-estagio";
import type { Orcamento } from "@/domain/entities/orcamento";
import { rotuloDoEstagio, type Estagio } from "@/domain/value-objects/estagio-atendimento";
import { cn } from "@/lib/utils";

import { CartaoOrcamento } from "./cartao-orcamento";

/** Como a coluna aparece enquanto um card é arrastado (destaca os destinos válidos). */
export type Destaque = "origem" | "valida" | "invalida" | null;

interface Props {
  estagio: Estagio;
  cards: Orcamento[];
  destaque: Destaque;
  terminal: boolean;
  aoAbrir: (id: string) => void;
}

export function Coluna({ estagio, cards, destaque, terminal, aoAbrir }: Props) {
  const { setNodeRef, isOver } = useDroppable({ id: estagio });
  const rotulo = rotuloDoEstagio(estagio);
  const quantidade = `${cards.length} ${cards.length === 1 ? "orçamento" : "orçamentos"}`;

  return (
    <section
      ref={setNodeRef}
      aria-label={`${rotulo}, ${quantidade}`}
      className={cn(
        "flex min-h-64 flex-col rounded-xl border bg-muted/40 transition-colors",
        destaque === "valida" && "border-primary/50 bg-primary/5",
        destaque === "valida" && isOver && "border-primary bg-primary/10",
        destaque === "invalida" && "opacity-50",
      )}
    >
      <header className="flex items-center gap-2 px-3 pt-3 pb-2">
        <span className={cn("size-2 rounded-full", COR_DO_ESTAGIO[estagio])} aria-hidden />
        <h2 className="text-sm font-semibold">{rotulo}</h2>
        <span className="ml-auto rounded-full bg-background px-2 text-xs tabular-nums text-muted-foreground">
          {cards.length}
        </span>
      </header>
      <ul className="flex flex-1 flex-col gap-2 p-2">
        {cards.map((card) => (
          <CartaoOrcamento key={card.id} card={card} podeArrastar={!terminal} aoAbrir={aoAbrir} />
        ))}
        {cards.length === 0 && (
          <li className="rounded-lg border border-dashed p-4 text-center text-xs text-muted-foreground">
            Nenhum orçamento
          </li>
        )}
      </ul>
    </section>
  );
}
