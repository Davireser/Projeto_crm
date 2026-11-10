"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { RegistrarContato } from "@/application/use-cases/registrar-contato";
import type { EntradaNovoContato } from "@/domain/entities/novo-contato";
import { paraCardDto } from "@/infra/http/mapeadores";
import { useApi, type PainelDto } from "@/lib/api/api-navegador";

import { CHAVE_PAINEL } from "./use-painel";

/** Cadastra cliente + primeiro orçamento; o card já entra no painel em cache (RF01). */
export function useRegistrarContato() {
  const api = useApi();
  const queryClient = useQueryClient();

  return useMutation({
    mutationKey: ["registrar-contato"],
    mutationFn: (entrada: EntradaNovoContato) => new RegistrarContato(api.clientes).executar(entrada),
    onSuccess: ({ orcamento }) => {
      queryClient.setQueryData<PainelDto>(
        CHAVE_PAINEL,
        (dto) => dto && { ...dto, cards: [...dto.cards, paraCardDto(orcamento)] },
      );
      void queryClient.invalidateQueries({ queryKey: CHAVE_PAINEL });
      toast.success(`Contato de ${orcamento.clienteNome} registrado.`);
    },
  });
}
