"use client";

import { useState, type FormEvent } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { AlteracaoUsuario } from "@/application/ports";
import type { ErrosPorCampo } from "@/domain/entities/novo-contato";
import {
  PERFIS,
  rotuloDoPerfil,
  TAMANHO_MINIMO_DA_SENHA,
  type Perfil,
  type Usuario,
} from "@/domain/entities/usuario";
import { useAlterarUsuario, useCriarUsuario } from "@/hooks/use-usuarios";
import { errosDoFormulario } from "@/lib/mensagens";

interface Props {
  solicitante: Usuario;
  /** `null` para criar; o usuário para editar nome, e-mail e perfil. */
  alvo: Usuario | null;
  aoConcluir: () => void;
}

/** Criação e edição de usuário. O domínio valida tudo e os erros aparecem por campo. */
export function FormUsuario({ solicitante, alvo, aoConcluir }: Props) {
  const criar = useCriarUsuario(solicitante);
  const alterar = useAlterarUsuario(solicitante);
  const [perfil, setPerfil] = useState<Perfil>(alvo?.perfil ?? "USUARIO");
  const [erros, setErros] = useState<ErrosPorCampo>({});
  const enviando = criar.isPending || alterar.isPending;

  function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    const dados = new FormData(evento.currentTarget);
    const texto = (campo: string) => String(dados.get(campo) ?? "");
    const aoFalhar = (erro: Error) => setErros(errosDoFormulario(erro));
    setErros({});

    if (!alvo) {
      criar.mutate(
        { nome: texto("nome"), email: texto("email"), senha: texto("senha"), perfil },
        {
          onSuccess: (criado) => {
            toast.success(`Usuário ${criado.nome} criado.`);
            aoConcluir();
          },
          onError: aoFalhar,
        },
      );
      return;
    }

    // Só envia o que mudou.
    const alteracao: AlteracaoUsuario = {};
    if (texto("nome") !== alvo.nome) alteracao.nome = texto("nome");
    if (texto("email") !== alvo.email) alteracao.email = texto("email");
    if (perfil !== alvo.perfil) alteracao.perfil = perfil;
    if (Object.keys(alteracao).length === 0) return aoConcluir();
    alterar.mutate(
      { alvo, alteracao },
      {
        onSuccess: (alterado) => {
          toast.success(`Dados de ${alterado.nome} salvos.`);
          aoConcluir();
        },
        onError: aoFalhar,
      },
    );
  }

  return (
    <form onSubmit={enviar} className="grid gap-4" noValidate>
      <Campo nome="nome" rotulo="Nome" erro={erros.nome} padrao={alvo?.nome} autoComplete="off" />
      <Campo nome="email" rotulo="E-mail" erro={erros.email} padrao={alvo?.email} type="email" autoComplete="off" />
      {!alvo && (
        <Campo
          nome="senha"
          rotulo="Senha"
          erro={erros.senha}
          type="password"
          autoComplete="new-password"
          dica={`Mínimo de ${TAMANHO_MINIMO_DA_SENHA} caracteres.`}
        />
      )}
      <fieldset className="grid gap-2">
        <legend className="mb-2 text-sm font-medium">Perfil</legend>
        <div className="flex gap-2">
          {PERFIS.map((opcao) => (
            <label
              key={opcao}
              className="flex cursor-pointer items-center gap-1.5 rounded-md border px-3 py-1.5 text-sm has-checked:border-primary has-checked:bg-primary/5"
            >
              <input
                type="radio"
                name="perfil"
                value={opcao}
                checked={perfil === opcao}
                onChange={() => setPerfil(opcao)}
                className="accent-primary"
              />
              {rotuloDoPerfil(opcao)}
            </label>
          ))}
        </div>
      </fieldset>
      {erros.geral && (
        <p role="alert" className="text-sm text-destructive">
          {erros.geral}
        </p>
      )}
      <Button type="submit" disabled={enviando}>
        {alvo ? "Salvar alterações" : "Criar usuário"}
      </Button>
    </form>
  );
}

interface PropsCampo {
  nome: string;
  rotulo: string;
  erro?: string;
  dica?: string;
  padrao?: string;
  type?: string;
  autoComplete?: string;
}

function Campo({ nome, rotulo, erro, dica, padrao, type = "text", autoComplete }: PropsCampo) {
  const id = `usuario-${nome}`;
  return (
    <div className="grid gap-2">
      <Label htmlFor={id}>{rotulo}</Label>
      <Input
        id={id}
        name={nome}
        type={type}
        defaultValue={padrao}
        autoComplete={autoComplete}
        aria-invalid={erro ? true : undefined}
        aria-describedby={erro ? `${id}-erro` : dica ? `${id}-dica` : undefined}
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
}
