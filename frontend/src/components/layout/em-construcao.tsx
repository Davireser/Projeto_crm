import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

/** Marcador das telas que ainda serão feitas nas próximas partes do plano. */
export function EmConstrucao({ titulo, parte, descricao }: { titulo: string; parte: string; descricao: string }) {
  return (
    <div className="grid gap-6">
      <h1 className="text-2xl font-semibold tracking-tight">{titulo}</h1>
      <Card className="border-dashed">
        <CardHeader>
          <CardTitle>Em construção — Parte {parte}</CardTitle>
          <CardDescription>{descricao}</CardDescription>
        </CardHeader>
      </Card>
    </div>
  );
}
