"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { montarColunas, type Painel } from "@/application/use-cases/consultar-painel";
import { DefinirValor } from "@/application/use-cases/definir-valor";
import { MoverEstagio } from "@/application/use-cases/mover-estagio";
import { RegistrarInteracao } from "@/application/use-cases/registrar-interacao";
import type { Orcamento } from "@/domain/entities/orcamento";
import { Funil } from "@/domain/funil/funil";
import type { Estagio } from "@/domain/value-objects/estagio-atendimento";
import type { TipoInteracao } from "@/domain/value-objects/tipo-interacao";
import { paraCardDto, paraOrcamento } from "@/infra/http/mapeadores";
import { useApi, type PainelDto } from "@/lib/api/api-navegador";
import { hojeNoNegocio } from "@/lib/datas";
import { mensagemDeErro } from "@/lib/mensagens";

export const CHAVE_PAINEL = ["painel"] as const;

/** O cache guarda o JSON (serializável para o modo offline); a tela recebe o domínio. */
function paraPainel(dto: PainelDto): Painel {
  return { funil: Funil.doMapa(dto.mapa), colunas: montarColunas(dto.cards.map(paraOrcamento)) };
}

function comCard(dto: PainelDto | undefined, card: Orcamento): PainelDto | undefined {
  return dto && { ...dto, cards: dto.cards.map((c) => (c.id === card.id ? paraCardDto(card) : c)) };
}

export function usePainel(inicial?: PainelDto) {
  const api = useApi();
  return useQuery({
    queryKey: CHAVE_PAINEL,
    queryFn: () => api.buscarPainel(),
    initialData: inicial,
    select: paraPainel,
  });
}

interface Movimento {
  card: Orcamento;
  destino: Estagio;
  funil: Funil;
}

/**
 * Mover estágio com atualização otimista (RNF02): o card muda de coluna na hora;
 * se o backend recusar, volta para onde estava e o motivo aparece num aviso.
 */
export function useMoverEstagio() {
  const api = useApi();
  const queryClient = useQueryClient();

  return useMutation({
    mutationKey: ["mover-estagio"],
    mutationFn: ({ card, destino, funil }: Movimento) =>
      new MoverEstagio(api.orcamentos).executar(card, destino, funil),
    onMutate: async ({ card, destino, funil }) => {
      await queryClient.cancelQueries({ queryKey: CHAVE_PAINEL });
      const anterior = queryClient.getQueryData<PainelDto>(CHAVE_PAINEL);
      queryClient.setQueryData<PainelDto>(CHAVE_PAINEL, (dto) =>
        comCard(dto, card.moverPara(destino, funil, hojeNoNegocio())),
      );
      return { anterior };
    },
    onError: (erro, _movimento, contexto) => {
      if (contexto?.anterior) queryClient.setQueryData(CHAVE_PAINEL, contexto.anterior);
      toast.error(mensagemDeErro(erro));
    },
    onSuccess: (confirmado) => {
      queryClient.setQueryData<PainelDto>(CHAVE_PAINEL, (dto) => comCard(dto, confirmado));
    },
    onSettled: () => queryClient.invalidateQueries({ queryKey: CHAVE_PAINEL }),
  });
}

/** Ponto único de movimento (arraste e botões): o domínio decide antes de qualquer chamada. */
export function useTentarMover() {
  const mover = useMoverEstagio();

  return (card: Orcamento, destino: Estagio, funil: Funil): boolean => {
    if (destino === card.estagio) return false;
    const motivo = card.motivoParaNaoMover(destino, funil);
    if (motivo) {
      toast.error(motivo);
      return false;
    }
    mover.mutate({ card, destino, funil });
    return true;
  };
}

export function useDefinirValor() {
  const api = useApi();
  const queryClient = useQueryClient();

  return useMutation({
    mutationKey: ["definir-valor"],
    mutationFn: ({ card, texto, funil }: { card: Orcamento; texto: string; funil: Funil }) =>
      new DefinirValor(api.orcamentos).executar(card, texto, funil),
    onSuccess: (atualizado) => {
      queryClient.setQueryData<PainelDto>(CHAVE_PAINEL, (dto) => comCard(dto, atualizado));
      toast.success("Valor salvo.");
    },
    onSettled: () => queryClient.invalidateQueries({ queryKey: CHAVE_PAINEL }),
  });
}

export function useRegistrarInteracao() {
  const api = useApi();
  const queryClient = useQueryClient();

  return useMutation({
    mutationKey: ["registrar-interacao"],
    mutationFn: ({ card, tipo, conteudo }: { card: Orcamento; tipo: TipoInteracao; conteudo: string }) =>
      new RegistrarInteracao(api.orcamentos).executar(card.id, tipo, conteudo),
    onSuccess: (_interacao, { card }) => {
      queryClient.setQueryData<PainelDto>(CHAVE_PAINEL, (dto) => {
        const atual = dto?.cards.find((c) => c.id === card.id);
        return atual ? comCard(dto, paraOrcamento(atual).comNovaInteracao()) : dto;
      });
      void queryClient.invalidateQueries({ queryKey: ["cliente", card.clienteId] });
      toast.success("Interação registrada.");
    },
  });
}
