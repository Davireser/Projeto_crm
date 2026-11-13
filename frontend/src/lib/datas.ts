/** Fuso do negócio, o mesmo padrão do backend (FUSO_HORARIO). */
export const FUSO_DO_NEGOCIO = "America/Sao_Paulo";

const DIA_ISO = new Intl.DateTimeFormat("en-CA", {
  timeZone: FUSO_DO_NEGOCIO,
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
});

const DATA_HORA = new Intl.DateTimeFormat("pt-BR", {
  timeZone: FUSO_DO_NEGOCIO,
  dateStyle: "short",
  timeStyle: "short",
});

/** Data de hoje (`AAAA-MM-DD`) no fuso do negócio. */
export function hojeNoNegocio(agora: Date = new Date()): string {
  return DIA_ISO.format(agora);
}

/** `2026-09-01` → `01/09/2026`, sem passar por `Date` (que deslocaria o dia pelo fuso). */
export function formatarData(dataIso: string): string {
  const [ano, mes, dia] = dataIso.split("-");
  return `${dia}/${mes}/${ano}`;
}

/** Instante UTC da API mostrado no horário de São Paulo. */
export function formatarDataHora(instanteIso: string): string {
  return DATA_HORA.format(new Date(instanteIso));
}
