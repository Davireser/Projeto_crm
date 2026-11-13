"use client";

import { RotateCcw } from "lucide-react";
import Link from "next/link";
import { useId, useState, type FormEvent } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Textarea } from "@/components/ui/textarea";
import type { Orcamento } from "@/domain/entities/orcamento";
import type { Funil } from "@/domain/funil/funil";
import { rotuloDoEstagio } from "@/domain/value-objects/estagio-atendimento";
import {
  TIPOS_DE_INTERACAO,
  rotuloDoTipo,
  type TipoInteracao,
} from "@/domain/value-objects/tipo-interacao";
import {
  useDefinirValor,
  useReabrirAtendimento,
  useRegistrarInteracao,
  useTentarMover,
} from "@/hooks/use-painel";
import { formatarData } from "@/lib/datas";
import { mensagemDeErro } from "@/lib/mensagens";

interface Props {
  card: Orcamento | null;
  funil: Funil;
  aoFechar: () => void;
  /** Troca o orçamento mostrado (ex.: o novo, depois de reabrir o atendimento). */
  aoAbrir: (id: string) => void;
}

/** Gaveta com os detalhes do orçamento: mover, definir valor e registrar interação. */
export function DetalheOrcamento({ card, funil, aoFechar, aoAbrir }: Props) {
  return (
    <Sheet open={card !== null} onOpenChange={(aberto) => !aberto && aoFechar()}>
      <SheetContent className="w-full overflow-y-auto sm:max-w-md">
        {card && <Conteudo card={card} funil={funil} aoAbrir={aoAbrir} />}
      </SheetContent>
    </Sheet>
  );
}

function Conteudo({ card, funil, aoAbrir }: { card: Orcamento; funil: Funil; aoAbrir: (id: string) => void }) {
  const encerrado = !card.estaEmAberto(funil);

  return (
    <>
      <SheetHeader>
        <SheetTitle>{card.clienteNome}</SheetTitle>
        <SheetDescription className="flex flex-wrap items-center gap-2">
          <Badge variant="secondary">{rotuloDoEstagio(card.estagio)}</Badge>
          <span>Aberto em {formatarData(card.dataAbertura)}</span>
          {card.dataFechamento && <span>· Encerrado em {formatarData(card.dataFechamento)}</span>}
        </SheetDescription>
      </SheetHeader>
      <div className="grid gap-6 px-4 pb-6">
        <Movimentos card={card} funil={funil} />
        {card.podeReabrirAtendimento() && <ReabrirAtendimento card={card} aoAbrir={aoAbrir} />}
        <Separator />
        {encerrado ? (
          <section className="grid gap-1">
            <h3 className="text-sm font-medium">Valor</h3>
            <p className="text-sm">{card.valor?.formatado() ?? "Sem valor"}</p>
          </section>
        ) : (
          <FormValor key={card.valor?.paraApi() ?? "sem-valor"} card={card} funil={funil} />
        )}
        <Separator />
        <FormInteracao card={card} />
        <Button asChild variant="outline">
          <Link href={`/clientes/${card.clienteId}`}>Ver cliente e histórico</Link>
        </Button>
      </div>
    </>
  );
}

function Movimentos({ card, funil }: { card: Orcamento; funil: Funil }) {
  const tentarMover = useTentarMover();
  const destinos = funil.destinosDe(card.estagio);

  return (
    <section className="grid gap-2">
      <h3 className="text-sm font-medium">Mover para</h3>
      {destinos.length === 0 ? (
        <p className="text-sm text-muted-foreground">Orçamento encerrado.</p>
      ) : (
        <div className="flex flex-wrap gap-2">
          {destinos.map((destino) => (
            <Button
              key={destino}
              size="sm"
              variant={destino === "PERDIDO" ? "outline" : "default"}
              aria-label={`Mover para ${rotuloDoEstagio(destino)}`}
              onClick={() => tentarMover(card, destino, funil)}
            >
              {rotuloDoEstagio(destino)}
            </Button>
          ))}
        </div>
      )}
    </section>
  );
}

function ReabrirAtendimento({ card, aoAbrir }: { card: Orcamento; aoAbrir: (id: string) => void }) {
  const reabrir = useReabrirAtendimento();

  return (
    <section className="grid gap-2 rounded-lg border border-dashed p-3">
      <h3 className="text-sm font-medium">Cliente voltou a ter interesse?</h3>
      <p className="text-sm text-muted-foreground">
        Abre um novo orçamento em Novo contato. Este continua como perdido no histórico e nas métricas.
      </p>
      <Button
        size="sm"
        variant="secondary"
        className="w-fit"
        disabled={reabrir.isPending}
        onClick={() => reabrir.mutate(card, { onSuccess: (novo) => aoAbrir(novo.id) })}
      >
        <RotateCcw aria-hidden /> Reabrir atendimento
      </Button>
    </section>
  );
}

function FormValor({ card, funil }: { card: Orcamento; funil: Funil }) {
  const definir = useDefinirValor();
  const id = useId();

  function salvar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    const texto = String(new FormData(evento.currentTarget).get("valor") ?? "");
    definir.mutate({ card, texto, funil });
  }

  return (
    <form onSubmit={salvar} className="grid gap-2" noValidate>
      <Label htmlFor={id}>Valor (R$)</Label>
      <div className="flex gap-2">
        <Input
          id={id}
          name="valor"
          inputMode="decimal"
          placeholder="Ex.: 4.200,00"
          defaultValue={card.valor?.paraApi().replace(".", ",") ?? ""}
          aria-invalid={definir.isError}
          aria-describedby={definir.isError ? `${id}-erro` : undefined}
        />
        <Button type="submit" variant="secondary" disabled={definir.isPending}>
          Salvar valor
        </Button>
      </div>
      {definir.isError && (
        <p id={`${id}-erro`} className="text-sm text-destructive">
          {mensagemDeErro(definir.error)}
        </p>
      )}
    </form>
  );
}

function FormInteracao({ card }: { card: Orcamento }) {
  const registrar = useRegistrarInteracao();
  const [tipo, setTipo] = useState<TipoInteracao>("MENSAGEM");
  const [conteudo, setConteudo] = useState("");
  const id = useId();

  function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    registrar.mutate({ card, tipo, conteudo }, { onSuccess: () => setConteudo("") });
  }

  return (
    <form onSubmit={enviar} className="grid gap-3" noValidate>
      <fieldset className="grid gap-2">
        <legend className="mb-2 text-sm font-medium">Registrar interação</legend>
        <div className="flex gap-2" role="radiogroup" aria-label="Tipo de interação">
          {TIPOS_DE_INTERACAO.map((opcao) => (
            <label
              key={opcao}
              className="flex cursor-pointer items-center gap-1.5 rounded-md border px-3 py-1.5 text-sm has-checked:border-primary has-checked:bg-primary/5"
            >
              <input
                type="radio"
                name="tipo"
                value={opcao}
                checked={tipo === opcao}
                onChange={() => setTipo(opcao)}
                className="accent-primary"
              />
              {rotuloDoTipo(opcao)}
            </label>
          ))}
        </div>
      </fieldset>
      <div className="grid gap-2">
        <Label htmlFor={id}>O que foi conversado</Label>
        <Textarea
          id={id}
          value={conteudo}
          onChange={(e) => setConteudo(e.target.value)}
          rows={3}
          aria-invalid={registrar.isError}
        />
      </div>
      {registrar.isError && (
        <p className="text-sm text-destructive">{mensagemDeErro(registrar.error)}</p>
      )}
      <Button type="submit" disabled={registrar.isPending}>
        Registrar interação
      </Button>
    </form>
  );
}
