import { Building2, Mail, MessageSquare, Package, Phone, Users, type LucideIcon } from "lucide-react";
import type { ReactNode } from "react";

import type { DetalheCliente } from "@/application/use-cases/consultar-cliente";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { rotuloDoEstagio } from "@/domain/value-objects/estagio-atendimento";
import { rotuloDoTipo, type TipoInteracao } from "@/domain/value-objects/tipo-interacao";
import { formatarData, formatarDataHora } from "@/lib/datas";

const ICONE_DO_TIPO: Record<TipoInteracao, LucideIcon> = {
  MENSAGEM: MessageSquare,
  LIGACAO: Phone,
  REUNIAO: Users,
};

const plural = (n: number, singular: string, plural: string) => `${n} ${n === 1 ? singular : plural}`;

/** Dados do cliente, seus orçamentos (RF08) e a linha do tempo de interações (RF07). */
export function FichaCliente({ detalhe }: { detalhe: DetalheCliente }) {
  const { cliente, orcamentos, historico } = detalhe;
  const aberturaDo = new Map(orcamentos.map((o) => [o.id, o.dataAbertura]));
  const recentesPrimeiro = [...historico].sort((a, b) =>
    b.interacao.dataHora.localeCompare(a.interacao.dataHora),
  );

  return (
    <div className="grid gap-6">
      <header className="grid gap-1">
        <h1 className="text-2xl font-semibold tracking-tight">{cliente.nome}</h1>
        <p className="text-sm text-muted-foreground">
          {plural(orcamentos.length, "orçamento", "orçamentos")} ·{" "}
          {plural(historico.length, "interação", "interações")}
        </p>
      </header>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,2fr)]">
        <div className="grid content-start gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Contato</CardTitle>
            </CardHeader>
            <CardContent>
              <dl className="grid gap-3 text-sm">
                <Dado icone={Phone} rotulo="Telefone">
                  <a href={`tel:+55${cliente.telefone.numero}`} className="hover:underline">
                    {cliente.telefone.formatado()}
                  </a>
                </Dado>
                <Dado icone={Mail} rotulo="E-mail">
                  <a href={`mailto:${cliente.email.endereco}`} className="break-all hover:underline">
                    {cliente.email.endereco}
                  </a>
                </Dado>
                {cliente.empresa && (
                  <Dado icone={Building2} rotulo="Empresa">
                    {cliente.empresa}
                  </Dado>
                )}
                {cliente.tipoEmbalagemInteresse && (
                  <Dado icone={Package} rotulo="Embalagem de interesse">
                    {cliente.tipoEmbalagemInteresse}
                  </Dado>
                )}
              </dl>
            </CardContent>
          </Card>

          <section aria-labelledby="titulo-orcamentos" className="grid gap-3">
            <h2 id="titulo-orcamentos" className="text-lg font-semibold">
              Orçamentos
            </h2>
            <ul className="grid gap-2">
              {orcamentos.map((o) => (
                <li key={o.id} className="grid gap-1 rounded-lg border bg-card p-3 text-sm">
                  <div className="flex items-center justify-between gap-2">
                    <Badge variant="secondary">{rotuloDoEstagio(o.estagio)}</Badge>
                    <span className={o.valor ? "font-semibold tabular-nums" : "text-muted-foreground"}>
                      {o.valor?.formatado() ?? "Sem valor"}
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Aberto em {formatarData(o.dataAbertura)}
                    {o.dataFechamento && ` · Encerrado em ${formatarData(o.dataFechamento)}`}
                  </p>
                </li>
              ))}
            </ul>
          </section>
        </div>

        <section aria-labelledby="titulo-historico" className="grid content-start gap-3">
          <h2 id="titulo-historico" className="text-lg font-semibold">
            Histórico de interações
          </h2>
          {recentesPrimeiro.length === 0 ? (
            <p className="text-sm text-muted-foreground">Nenhuma interação registrada ainda.</p>
          ) : (
            <ol aria-label="Linha do tempo" className="grid gap-4 border-l pl-6">
              {recentesPrimeiro.map(({ orcamentoId, interacao }) => {
                const Icone = ICONE_DO_TIPO[interacao.tipo];
                const abertura = aberturaDo.get(orcamentoId);
                return (
                  <li key={interacao.id} className="relative grid gap-1">
                    <span className="absolute top-0 -left-[2.3rem] grid size-6 place-items-center rounded-full border bg-background">
                      <Icone className="size-3.5 text-muted-foreground" aria-hidden />
                    </span>
                    <p className="flex flex-wrap items-baseline gap-x-2 text-sm">
                      <span className="font-medium">{rotuloDoTipo(interacao.tipo)}</span>
                      <time dateTime={interacao.dataHora} className="text-xs text-muted-foreground">
                        {formatarDataHora(interacao.dataHora)}
                      </time>
                      {orcamentos.length > 1 && abertura && (
                        <span className="text-xs text-muted-foreground">
                          · orçamento aberto em {formatarData(abertura)}
                        </span>
                      )}
                    </p>
                    <p className="text-sm whitespace-pre-line">{interacao.conteudo}</p>
                  </li>
                );
              })}
            </ol>
          )}
        </section>
      </div>
    </div>
  );
}

function Dado({ icone: Icone, rotulo, children }: { icone: LucideIcon; rotulo: string; children: ReactNode }) {
  return (
    <div className="flex items-start gap-3">
      <Icone className="mt-0.5 size-4 shrink-0 text-muted-foreground" aria-hidden />
      <div className="grid">
        <dt className="text-xs text-muted-foreground">{rotulo}</dt>
        <dd>{children}</dd>
      </div>
    </div>
  );
}
