"use client";

import {
  DndContext,
  DragOverlay,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
  type DragStartEvent,
} from "@dnd-kit/core";
import { Plus, Search } from "lucide-react";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ESTAGIOS } from "@/domain/value-objects/estagio-atendimento";
import { usePainel, useTentarMover } from "@/hooks/use-painel";
import type { PainelDto } from "@/lib/api/api-navegador";
import { mensagemDeErro } from "@/lib/mensagens";

import { ConteudoCartao } from "./cartao-orcamento";
import { Coluna } from "./coluna";
import { DetalheOrcamento } from "./detalhe-orcamento";
import { EsqueletoKanban } from "./esqueleto-kanban";
import { avisosDoArraste, destaqueDa, estagioDoDestino, filtrar } from "./logica-do-painel";
import { StatusConexao } from "./status-conexao";

/** Painel Kanban do funil (RF05) com arraste entre estágios (RF02, RNF02). */
export function Kanban({ inicial }: { inicial?: PainelDto }) {
  const { data: painel, error } = usePainel(inicial);
  const tentarMover = useTentarMover();
  const [busca, setBusca] = useState("");
  const [arrastandoId, setArrastandoId] = useState<string | null>(null);
  const [abertoId, setAbertoId] = useState<string | null>(null);
  const sensores = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 6 } }),
    useSensor(KeyboardSensor),
  );

  // Com cacheComponents, o Next esconde a página ao navegar (<Activity>) em vez de desmontá-la, e o
  // estado volta junto. A gaveta é modal: fecha ao sair de cena para não reaparecer na volta.
  useEffect(() => () => setAbertoId(null), []);

  const porId = useMemo(
    () => new Map(ESTAGIOS.flatMap((e) => painel?.colunas[e] ?? []).map((c) => [c.id, c])),
    [painel],
  );

  if (!painel) {
    if (error) {
      return (
        <p role="alert" className="text-destructive">
          Não foi possível carregar o painel. {mensagemDeErro(error)}
        </p>
      );
    }
    return <EsqueletoKanban />;
  }

  const { funil } = painel;
  const arrastando = arrastandoId ? (porId.get(arrastandoId) ?? null) : null;
  const colunas = filtrar(painel.colunas, busca);
  const total = porId.size;

  function aoSoltar({ active, over }: DragEndEvent) {
    setArrastandoId(null);
    const card = porId.get(String(active.id));
    const destino = estagioDoDestino(over?.id);
    if (card && destino) tentarMover(card, destino, funil);
  }

  return (
    <div className="grid gap-4">
      <div className="flex flex-wrap items-center gap-3">
        <h1 className="text-2xl font-semibold tracking-tight">Painel</h1>
        <span className="text-sm text-muted-foreground">
          {total} {total === 1 ? "orçamento" : "orçamentos"}
        </span>
        <StatusConexao />
        <div className="ml-auto flex items-center gap-2">
          <div className="relative">
            <Search className="absolute top-2.5 left-2.5 size-4 text-muted-foreground" aria-hidden />
            <Input
              type="search"
              aria-label="Buscar cliente"
              placeholder="Buscar cliente"
              value={busca}
              onChange={(e) => setBusca(e.target.value)}
              className="w-48 pl-8 sm:w-64"
            />
          </div>
          <Button asChild>
            <Link href="/contatos/novo">
              <Plus aria-hidden /> Novo contato
            </Link>
          </Button>
        </div>
      </div>

      <DndContext
        sensors={sensores}
        accessibility={{
          announcements: avisosDoArraste(porId),
          screenReaderInstructions: {
            draggable:
              "Para mover, pressione Espaço. Use as setas para escolher a coluna e Espaço de novo para soltar. Esc cancela.",
          },
        }}
        onDragStart={({ active }: DragStartEvent) => setArrastandoId(String(active.id))}
        onDragEnd={aoSoltar}
        onDragCancel={() => setArrastandoId(null)}
      >
        <div className="grid auto-cols-[minmax(14rem,1fr)] grid-flow-col gap-4 overflow-x-auto pb-2">
          {ESTAGIOS.map((estagio) => (
            <Coluna
              key={estagio}
              estagio={estagio}
              cards={colunas[estagio]}
              destaque={destaqueDa(estagio, arrastando, funil)}
              terminal={funil.ehTerminal(estagio)}
              aoAbrir={setAbertoId}
            />
          ))}
        </div>
        <DragOverlay>
          {arrastando && (
            <div className="grid cursor-grabbing gap-0.5 rounded-lg border bg-card p-3 shadow-lg">
              <ConteudoCartao card={arrastando} />
            </div>
          )}
        </DragOverlay>
      </DndContext>

      <DetalheOrcamento
        card={abertoId ? (porId.get(abertoId) ?? null) : null}
        funil={funil}
        aoFechar={() => setAbertoId(null)}
        aoAbrir={setAbertoId}
      />
    </div>
  );
}
