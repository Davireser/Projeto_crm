export const TIPOS_DE_INTERACAO = ["MENSAGEM", "LIGACAO", "REUNIAO"] as const;

export type TipoInteracao = (typeof TIPOS_DE_INTERACAO)[number];

const ROTULOS: Record<TipoInteracao, string> = {
  MENSAGEM: "Mensagem",
  LIGACAO: "Ligação",
  REUNIAO: "Reunião",
};

export function rotuloDoTipo(tipo: TipoInteracao): string {
  return ROTULOS[tipo];
}
