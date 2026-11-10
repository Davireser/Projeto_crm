import { ArrowLeft } from "lucide-react";
import type { Metadata } from "next";
import Link from "next/link";
import { notFound, redirect } from "next/navigation";
import { cache, Suspense } from "react";

import { ErroRemoto } from "@/application/errors";
import { ConsultarCliente, type DetalheCliente } from "@/application/use-cases/consultar-cliente";
import { FichaCliente } from "@/components/clientes/ficha-cliente";
import { Skeleton } from "@/components/ui/skeleton";
import { ClienteGatewayHttp } from "@/infra/http/gateways-http";
import { apiDoServidor } from "@/lib/sessao/servidor";

/** Uma busca por requisição, compartilhada entre a página e o `generateMetadata`. */
const carregarCliente = cache(async (id: string): Promise<DetalheCliente> => {
  try {
    return await new ConsultarCliente(new ClienteGatewayHttp(await apiDoServidor())).executar(id);
  } catch (erro) {
    if (erro instanceof ErroRemoto && erro.sessaoExpirada) redirect(`/login?de=/clientes/${id}`);
    // 404, ou um id que nem é UUID (422): para quem navega, é um cliente que não existe.
    if (erro instanceof ErroRemoto && (erro.status === 404 || erro.status === 422)) notFound();
    throw erro;
  }
});

export async function generateMetadata({ params }: PageProps<"/clientes/[id]">): Promise<Metadata> {
  const { cliente } = await carregarCliente((await params).id);
  return {
    title: cliente.nome,
    description: `Contato, orçamentos e histórico de interações de ${cliente.nome}.`,
  };
}

export default function Pagina({ params }: PageProps<"/clientes/[id]">) {
  return (
    <div className="grid gap-4">
      <Link
        href="/painel"
        className="flex w-fit items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
      >
        <ArrowLeft className="size-4" aria-hidden /> Painel
      </Link>
      <Suspense fallback={<EsqueletoFicha />}>
        <FichaComDados params={params} />
      </Suspense>
    </div>
  );
}

async function FichaComDados({ params }: Pick<PageProps<"/clientes/[id]">, "params">) {
  return <FichaCliente detalhe={await carregarCliente((await params).id)} />;
}

function EsqueletoFicha() {
  return (
    <div className="grid gap-6" aria-busy="true" aria-label="Carregando cliente">
      <Skeleton className="h-8 w-64" />
      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,2fr)]">
        <Skeleton className="h-56" />
        <Skeleton className="h-72" />
      </div>
    </div>
  );
}
