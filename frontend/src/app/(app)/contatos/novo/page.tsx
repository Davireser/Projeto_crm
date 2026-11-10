import type { Metadata } from "next";

import { FormNovoContato } from "@/components/contatos/form-novo-contato";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export const metadata: Metadata = {
  title: "Novo contato",
  description: "Cadastro do cliente com o primeiro orçamento, que entra no funil em Novo contato.",
};

export default function Pagina() {
  return (
    <Card className="mx-auto w-full max-w-lg">
      <CardHeader>
        <CardTitle>
          <h1 className="text-xl">Novo contato</h1>
        </CardTitle>
        <CardDescription>O cliente entra no painel em &ldquo;Novo contato&rdquo;, com o primeiro orçamento aberto.</CardDescription>
      </CardHeader>
      <CardContent>
        <FormNovoContato />
      </CardContent>
    </Card>
  );
}
