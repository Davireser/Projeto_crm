"use client";

import { useDraggable } from "@dnd-kit/core";
import { GripVertical, MessageSquare } from "lucide-react";

import type { Orcamento } from "@/domain/entities/orcamento";
import { formatarData } from "@/lib/datas";
import { cn } from "@/lib/utils";

const plural = (n: number, singular: string, plural: string) => `${n} ${n === 1 ? singular : plural}`;

/** Conteúdo visual do card; usado também na sobreposição durante o arraste. */
export function ConteudoCartao({ card }: { card: Orcamento }) {
  return (
    <>
      <p className="truncate font-medium">{card.clienteNome}</p>
      <p className={cn("text-sm", card.valor ? "font-semibold tabular-nums" : "text-muted-foreground")}>
        {card.valor ? card.valor.formatado() : "Sem valor"}
      </p>
      <div className="mt-1 flex items-center justify-between text-xs text-muted-foreground">
        <span>
          {card.dataFechamento
            ? `Encerrado em ${formatarData(card.dataFechamento)}`
            : `Aberto em ${formatarData(card.dataAbertura)}`}
        </span>
        <span className="flex items-center gap-1" aria-label={plural(card.qtdInteracoes, "interação", "interações")}>
          <MessageSquare className="size-3" aria-hidden />
          {card.qtdInteracoes}
        </span>
      </div>
    </>
  );
}

interface Props {
  card: Orcamento;
  podeArrastar: boolean;
  aoAbrir: (id: string) => void;
}

/**
 * Card do Kanban. O mouse arrasta pelo card inteiro; pelo teclado, a alça
 * (Espaço para pegar, setas para escolher a coluna, Espaço para soltar).
 * Clicar abre os detalhes.
 */
export function CartaoOrcamento({ card, podeArrastar, aoAbrir }: Props) {
  const { setNodeRef, setActivatorNodeRef, listeners, attributes, isDragging } = useDraggable({
    id: card.id,
    disabled: !podeArrastar,
  });

  return (
    <li
      ref={setNodeRef}
      onPointerDown={(evento) => listeners?.onPointerDown?.(evento)}
      className={cn(
        "group relative rounded-lg border bg-card p-3 shadow-xs transition-shadow hover:shadow-sm",
        podeArrastar && "cursor-grab active:cursor-grabbing",
        isDragging && "opacity-40",
      )}
    >
      <button
        type="button"
        onClick={() => aoAbrir(card.id)}
        aria-label={`Abrir orçamento de ${card.clienteNome}`}
        className="absolute inset-0 rounded-lg focus-visible:outline-2 focus-visible:outline-ring"
      />
      <div className="pointer-events-none grid gap-0.5 pr-6">
        <ConteudoCartao card={card} />
      </div>
      {podeArrastar && (
        <button
          type="button"
          ref={setActivatorNodeRef}
          {...attributes}
          onKeyDown={(evento) => listeners?.onKeyDown?.(evento)}
          aria-label={`Mover orçamento de ${card.clienteNome}`}
          className="absolute top-2 right-1 rounded p-1 text-muted-foreground opacity-60 hover:bg-accent group-hover:opacity-100 focus-visible:opacity-100"
        >
          <GripVertical className="size-4" aria-hidden />
        </button>
      )}
    </li>
  );
}
