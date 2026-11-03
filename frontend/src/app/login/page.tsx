import type { Metadata } from "next";
import { Suspense } from "react";

import { FormLogin } from "@/components/sessao/form-login";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

import { entrar } from "./actions";

export const metadata: Metadata = {
  title: "Entrar",
  description: "Acesse o CRM de Atendimento e Orçamentos.",
};

export default function PaginaLogin({ searchParams }: PageProps<"/login">) {
  return (
    <main className="flex min-h-full flex-1 items-center justify-center bg-muted/40 p-4">
      <Card className="w-full max-w-sm">
        <CardHeader>
          <CardTitle className="text-xl">CRM de Orçamentos</CardTitle>
          <CardDescription>Entre com o seu e-mail e senha.</CardDescription>
        </CardHeader>
        <CardContent>
          <Suspense fallback={<FormLogin acao={entrar} de={null} />}>
            <FormComDestino searchParams={searchParams} />
          </Suspense>
        </CardContent>
      </Card>
    </main>
  );
}

/** Lê `?de=` (dado da requisição) dentro do Suspense, mantendo o resto da página estático. */
async function FormComDestino({ searchParams }: Pick<PageProps<"/login">, "searchParams">) {
  const { de } = await searchParams;
  return <FormLogin acao={entrar} de={typeof de === "string" ? de : null} />;
}
