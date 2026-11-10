import Link from "next/link";

import { Button } from "@/components/ui/button";

export default function ClienteNaoEncontrado() {
  return (
    <div className="mx-auto grid max-w-md justify-items-center gap-3 py-16 text-center">
      <h1 className="text-xl font-semibold">Cliente não encontrado</h1>
      <p className="text-sm text-muted-foreground">O link pode estar errado ou o cliente não existe mais.</p>
      <Button asChild variant="outline">
        <Link href="/painel">Voltar ao painel</Link>
      </Button>
    </div>
  );
}
