"use client";

import { Pencil, UserPlus } from "lucide-react";
import { useMemo, useState } from "react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { rotuloDoPerfil, Usuario, type DadosUsuario } from "@/domain/entities/usuario";
import { useAlterarUsuario, useUsuarios } from "@/hooks/use-usuarios";
import { mensagemDeErro } from "@/lib/mensagens";

import { FormUsuario } from "./form-usuario";

type Edicao = { tipo: "novo" } | { tipo: "editar"; usuario: Usuario } | null;

interface Props {
  /** Quem está logado; dados simples porque vêm do servidor. */
  solicitante: DadosUsuario;
  inicial?: DadosUsuario[];
}

/** Gestão de usuários (RF10): listar, criar, editar, ativar e desativar. Só administrador. */
export function GestaoUsuarios({ solicitante, inicial }: Props) {
  const eu = useMemo(() => new Usuario(solicitante), [solicitante]);
  const { data: usuarios, error } = useUsuarios(eu, inicial);
  const alterar = useAlterarUsuario(eu);
  const [edicao, setEdicao] = useState<Edicao>(null);

  function alternarAcesso(alvo: Usuario) {
    alterar.mutate(
      { alvo, alteracao: { ativo: !alvo.ativo } },
      {
        onSuccess: (alterado) =>
          toast.success(`Acesso de ${alterado.nome} ${alterado.ativo ? "reativado" : "desativado"}.`),
        onError: (erro) => toast.error(mensagemDeErro(erro)),
      },
    );
  }

  return (
    <div className="grid gap-4">
      <header className="flex flex-wrap items-center gap-3">
        <h1 className="text-2xl font-semibold tracking-tight">Usuários</h1>
        {usuarios && <span className="text-sm text-muted-foreground">{usuarios.length} cadastrados</span>}
        <Button className="ml-auto" onClick={() => setEdicao({ tipo: "novo" })}>
          <UserPlus aria-hidden /> Novo usuário
        </Button>
      </header>

      {error && !usuarios && (
        <p role="alert" className="text-destructive">
          Não foi possível carregar os usuários. {mensagemDeErro(error)}
        </p>
      )}

      {usuarios && (
        <div className="overflow-x-auto rounded-lg border">
          <table className="w-full text-sm">
            <thead className="bg-muted/50 text-left text-xs text-muted-foreground">
              <tr>
                <th scope="col" className="px-4 py-2 font-medium">Nome</th>
                <th scope="col" className="px-4 py-2 font-medium">E-mail</th>
                <th scope="col" className="px-4 py-2 font-medium">Perfil</th>
                <th scope="col" className="px-4 py-2 font-medium">Situação</th>
                <th scope="col" className="px-4 py-2 text-right font-medium">Ações</th>
              </tr>
            </thead>
            <tbody>
              {usuarios.map((usuario) => (
                <tr key={usuario.id} className="border-t">
                  <td className="px-4 py-3 font-medium">{usuario.nome}</td>
                  <td className="px-4 py-3 break-all text-muted-foreground">{usuario.email}</td>
                  <td className="px-4 py-3">
                    <Badge variant={usuario.perfil === "ADMINISTRADOR" ? "default" : "secondary"}>
                      {rotuloDoPerfil(usuario.perfil)}
                    </Badge>
                  </td>
                  <td className="px-4 py-3">
                    <Badge variant="outline" className={usuario.ativo ? "" : "text-muted-foreground"}>
                      <span
                        aria-hidden
                        className={`size-1.5 rounded-full ${usuario.ativo ? "bg-emerald-500" : "bg-muted-foreground"}`}
                      />
                      {usuario.ativo ? "Ativo" : "Inativo"}
                    </Badge>
                  </td>
                  <td className="px-4 py-3">
                    {eu.podeAlterarStatusDe(usuario) ? (
                      <div className="flex justify-end gap-2">
                        <Button
                          size="sm"
                          variant="ghost"
                          aria-label={`Editar ${usuario.nome}`}
                          onClick={() => setEdicao({ tipo: "editar", usuario })}
                        >
                          <Pencil aria-hidden /> Editar
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          aria-label={`${usuario.ativo ? "Desativar" : "Ativar"} ${usuario.nome}`}
                          disabled={alterar.isPending}
                          onClick={() => alternarAcesso(usuario)}
                        >
                          {usuario.ativo ? "Desativar" : "Ativar"}
                        </Button>
                      </div>
                    ) : (
                      <div className="flex justify-end">
                        <Badge variant="secondary">Você</Badge>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Sheet open={edicao !== null} onOpenChange={(aberto) => !aberto && setEdicao(null)}>
        <SheetContent className="w-full overflow-y-auto sm:max-w-md">
          {edicao && (
            <>
              <SheetHeader>
                <SheetTitle>{edicao.tipo === "novo" ? "Novo usuário" : `Editar ${edicao.usuario.nome}`}</SheetTitle>
                <SheetDescription>
                  {edicao.tipo === "novo"
                    ? "A pessoa entra com este e-mail e senha. Administradores também gerenciam usuários."
                    : "Para trocar a senha, use a ferramenta de redefinição no servidor."}
                </SheetDescription>
              </SheetHeader>
              <div className="px-4 pb-6">
                <FormUsuario
                  key={edicao.tipo === "novo" ? "novo" : edicao.usuario.id}
                  solicitante={eu}
                  alvo={edicao.tipo === "editar" ? edicao.usuario : null}
                  aoConcluir={() => setEdicao(null)}
                />
              </div>
            </>
          )}
        </SheetContent>
      </Sheet>
    </div>
  );
}
