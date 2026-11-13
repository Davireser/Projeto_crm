"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import type { AlteracaoUsuario } from "@/application/ports";
import { GerenciarUsuarios } from "@/application/use-cases/gerenciar-usuarios";
import { Usuario, type DadosUsuario, type EntradaNovoUsuario } from "@/domain/entities/usuario";
import { useApi } from "@/lib/api/api-navegador";

export const CHAVE_USUARIOS = ["usuarios"] as const;

const paraDados = (usuario: Usuario): DadosUsuario => ({ ...usuario });

/** Lista de usuários (RF10). O cache guarda dados simples; a tela recebe a entidade. */
export function useUsuarios(solicitante: Usuario, inicial?: DadosUsuario[]) {
  const api = useApi();
  return useQuery<DadosUsuario[], Error, Usuario[]>({
    queryKey: CHAVE_USUARIOS,
    queryFn: async () => (await new GerenciarUsuarios(api.usuarios).listar(solicitante)).map(paraDados),
    initialData: inicial,
    select: (lista) => lista.map((dados) => new Usuario(dados)),
  });
}

export function useCriarUsuario(solicitante: Usuario) {
  const api = useApi();
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: ["criar-usuario"],
    mutationFn: (entrada: EntradaNovoUsuario) => new GerenciarUsuarios(api.usuarios).criar(solicitante, entrada),
    onSuccess: (criado) =>
      queryClient.setQueryData<DadosUsuario[]>(CHAVE_USUARIOS, (lista = []) => [...lista, paraDados(criado)]),
  });
}

export function useAlterarUsuario(solicitante: Usuario) {
  const api = useApi();
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: ["alterar-usuario"],
    mutationFn: ({ alvo, alteracao }: { alvo: Usuario; alteracao: AlteracaoUsuario }) =>
      new GerenciarUsuarios(api.usuarios).alterar(solicitante, alvo, alteracao),
    onSuccess: (alterado) =>
      queryClient.setQueryData<DadosUsuario[]>(CHAVE_USUARIOS, (lista = []) =>
        lista.map((u) => (u.id === alterado.id ? paraDados(alterado) : u)),
      ),
  });
}
