"use client";

import { useActionState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ESTADO_INICIAL_LOGIN, type EstadoLogin } from "@/lib/sessao/estado-login";

interface Props {
  /** Server Action que autentica; recebida por props para ser testável. */
  acao: (estado: EstadoLogin, form: FormData) => Promise<EstadoLogin>;
  /** Página para voltar depois do login. */
  de: string | null;
}

export function FormLogin({ acao, de }: Props) {
  const [estado, enviar, enviando] = useActionState(acao, ESTADO_INICIAL_LOGIN);

  return (
    <form action={enviar} className="grid gap-4" noValidate>
      {de && <input type="hidden" name="de" value={de} />}
      <div className="grid gap-2">
        <Label htmlFor="email">E-mail</Label>
        <Input
          id="email"
          name="email"
          type="email"
          autoComplete="username"
          defaultValue={estado.email}
          key={estado.email}
          required
          aria-invalid={estado.erro !== null}
        />
      </div>
      <div className="grid gap-2">
        <Label htmlFor="senha">Senha</Label>
        <Input
          id="senha"
          name="senha"
          type="password"
          autoComplete="current-password"
          required
          aria-invalid={estado.erro !== null}
        />
      </div>
      {estado.erro && (
        <p role="alert" className="text-sm text-destructive">
          {estado.erro}
        </p>
      )}
      <Button type="submit" disabled={enviando} className="w-full">
        {enviando ? "Entrando…" : "Entrar"}
      </Button>
    </form>
  );
}
