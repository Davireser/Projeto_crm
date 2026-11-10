"use client";

import { useRouter } from "next/navigation";
import { useRef, useState, type ComponentProps, type FormEvent } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { EntradaNovoContato, ErrosPorCampo } from "@/domain/entities/novo-contato";
import { useRegistrarContato } from "@/hooks/use-registrar-contato";
import { errosDoFormulario } from "@/lib/mensagens";

type Campo = keyof EntradaNovoContato;

interface DefinicaoCampo {
  nome: Campo;
  rotulo: string;
  opcional?: boolean;
  dica?: string;
  props: ComponentProps<typeof Input>;
}

const CAMPOS: readonly DefinicaoCampo[] = [
  { nome: "nome", rotulo: "Nome", props: { autoComplete: "name" } },
  {
    nome: "telefone",
    rotulo: "Telefone",
    dica: "Com DDD, ex.: (31) 99876-5432",
    props: { type: "tel", inputMode: "tel", autoComplete: "tel" },
  },
  { nome: "email", rotulo: "E-mail", props: { type: "email", autoComplete: "email" } },
  { nome: "empresa", rotulo: "Empresa", opcional: true, props: { autoComplete: "organization" } },
  {
    nome: "tipoEmbalagemInteresse",
    rotulo: "Tipo de embalagem",
    opcional: true,
    dica: "Ex.: caixa de papelão, saco plástico",
    props: {},
  },
];

/**
 * Cadastro do cliente com o primeiro orçamento (RF01). O domínio valida tudo
 * antes de chamar a API e todos os erros aparecem juntos, cada um no seu campo (RF09).
 */
export function FormNovoContato() {
  const router = useRouter();
  const registrar = useRegistrarContato();
  const [erros, setErros] = useState<ErrosPorCampo>({});
  const formulario = useRef<HTMLFormElement>(null);

  function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    const dados = new FormData(evento.currentTarget);
    const texto = (campo: Campo) => String(dados.get(campo) ?? "");
    setErros({});
    registrar.mutate(
      {
        nome: texto("nome"),
        telefone: texto("telefone"),
        email: texto("email"),
        empresa: texto("empresa"),
        tipoEmbalagemInteresse: texto("tipoEmbalagemInteresse"),
      },
      {
        onSuccess: () => router.push("/painel"),
        onError: (erro) => {
          const novos = errosDoFormulario(erro);
          setErros(novos);
          const primeiro = CAMPOS.find((c) => novos[c.nome]);
          if (primeiro) {
            formulario.current?.querySelector<HTMLInputElement>(`[name="${primeiro.nome}"]`)?.focus();
          }
        },
      },
    );
  }

  function limparErro(campo: Campo) {
    if (erros[campo]) setErros(({ [campo]: _removido, ...resto }) => resto);
  }

  return (
    <form ref={formulario} onSubmit={enviar} className="grid gap-4" noValidate>
      {CAMPOS.map(({ nome, rotulo, opcional, dica, props }) => {
        const erro = erros[nome];
        const id = `campo-${nome}`;
        return (
          <div key={nome} className="grid gap-2">
            <Label htmlFor={id}>
              {rotulo}
              {opcional && <span className="font-normal text-muted-foreground">(opcional)</span>}
            </Label>
            <Input
              id={id}
              name={nome}
              {...props}
              required={!opcional}
              aria-invalid={erro ? true : undefined}
              aria-describedby={erro ? `${id}-erro` : dica ? `${id}-dica` : undefined}
              onChange={() => limparErro(nome)}
            />
            {erro ? (
              <p id={`${id}-erro`} className="text-sm text-destructive">
                {erro}
              </p>
            ) : (
              dica && (
                <p id={`${id}-dica`} className="text-xs text-muted-foreground">
                  {dica}
                </p>
              )
            )}
          </div>
        );
      })}
      {erros.geral && (
        <p role="alert" className="text-sm text-destructive">
          {erros.geral}
        </p>
      )}
      {registrar.isPaused && (
        <p role="status" className="text-sm text-amber-700 dark:text-amber-400">
          Sem conexão. O contato será enviado quando a rede voltar.
        </p>
      )}
      <Button type="submit" disabled={registrar.isPending}>
        {registrar.isPending ? "Salvando…" : "Registrar contato"}
      </Button>
    </form>
  );
}
