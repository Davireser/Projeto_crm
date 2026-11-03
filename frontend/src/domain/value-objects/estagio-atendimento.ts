/** Os cinco estágios do funil, na ordem das colunas do Kanban. Conjunto fechado. */
export const ESTAGIOS = [
  "NOVO_CONTATO",
  "EM_NEGOCIACAO",
  "ORCAMENTO_ENVIADO",
  "FECHADO",
  "PERDIDO",
] as const;

export type Estagio = (typeof ESTAGIOS)[number];

const ROTULOS: Record<Estagio, string> = {
  NOVO_CONTATO: "Novo contato",
  EM_NEGOCIACAO: "Em negociação",
  ORCAMENTO_ENVIADO: "Orçamento enviado",
  FECHADO: "Fechado",
  PERDIDO: "Perdido",
};

export const EstagioAtendimento = {
  NOVO_CONTATO: "NOVO_CONTATO",
  EM_NEGOCIACAO: "EM_NEGOCIACAO",
  ORCAMENTO_ENVIADO: "ORCAMENTO_ENVIADO",
  FECHADO: "FECHADO",
  PERDIDO: "PERDIDO",

  eh(valor: string): valor is Estagio {
    return (ESTAGIOS as readonly string[]).includes(valor);
  },
} as const;

export function rotuloDoEstagio(estagio: Estagio): string {
  return ROTULOS[estagio];
}
