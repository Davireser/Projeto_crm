import type { Announcements } from "@dnd-kit/core";

import type { Colunas } from "@/application/use-cases/consultar-painel";
import type { Orcamento } from "@/domain/entities/orcamento";
import type { Funil } from "@/domain/funil/funil";
import {
  ESTAGIOS,
  EstagioAtendimento,
  rotuloDoEstagio,
  type Estagio,
} from "@/domain/value-objects/estagio-atendimento";

import type { Destaque } from "./coluna";

/** Regras de tela do painel, separadas do React para serem testadas sem arrastar de verdade. */

const normalizar = (texto: string) =>
  texto.normalize("NFD").replace(/\p{Diacritic}/gu, "").toLowerCase().trim();

/** Busca pelo nome do cliente, sem diferenciar maiúsculas nem acentos. */
export function filtrar(colunas: Colunas, busca: string): Colunas {
  const termo = normalizar(busca);
  if (!termo) return colunas;
  return Object.fromEntries(
    ESTAGIOS.map((e) => [e, colunas[e].filter((c) => normalizar(c.clienteNome).includes(termo))]),
  ) as Colunas;
}

/** Enquanto um card é arrastado, cada coluna mostra se aceita o card (RN01/RN02). */
export function destaqueDa(coluna: Estagio, arrastando: Orcamento | null, funil: Funil): Destaque {
  if (!arrastando) return null;
  if (coluna === arrastando.estagio) return "origem";
  return arrastando.motivoParaNaoMover(coluna, funil) ? "invalida" : "valida";
}

/** O id de destino do dnd-kit é o estágio da coluna; qualquer outra coisa é ignorada. */
export function estagioDoDestino(id: string | number | undefined): Estagio | null {
  const texto = id === undefined ? "" : String(id);
  return EstagioAtendimento.eh(texto) ? texto : null;
}

/** Avisos em português para leitores de tela durante o arraste. */
export function avisosDoArraste(porId: ReadonlyMap<string, Orcamento>): Announcements {
  const nome = (id: string | number) => porId.get(String(id))?.clienteNome ?? "orçamento";
  const coluna = (id: string | number | undefined) => {
    const estagio = estagioDoDestino(id);
    return estagio && rotuloDoEstagio(estagio);
  };
  return {
    onDragStart: ({ active }) => `Movendo o orçamento de ${nome(active.id)}.`,
    onDragOver: ({ active, over }) =>
      coluna(over?.id) ? `${nome(active.id)} sobre a coluna ${coluna(over?.id)}.` : undefined,
    onDragEnd: ({ active, over }) =>
      coluna(over?.id)
        ? `${nome(active.id)} solto na coluna ${coluna(over?.id)}.`
        : `${nome(active.id)} não foi movido.`,
    onDragCancel: ({ active }) => `Movimento de ${nome(active.id)} cancelado.`,
  };
}
