import { Orcamento } from "@/domain/entities/orcamento";
import { Funil, type MapaDeTransicoes } from "@/domain/funil/funil";
import type { Estagio } from "@/domain/value-objects/estagio-atendimento";
import { ValorOrcado } from "@/domain/value-objects/valor-orcado";

/** O mesmo JSON que GET /api/v1/orcamentos/transicoes devolve. */
export const MAPA_DA_API: MapaDeTransicoes = {
  transicoes: {
    NOVO_CONTATO: ["EM_NEGOCIACAO", "PERDIDO"],
    EM_NEGOCIACAO: ["ORCAMENTO_ENVIADO", "PERDIDO"],
    ORCAMENTO_ENVIADO: ["FECHADO", "PERDIDO"],
    FECHADO: [],
    PERDIDO: [],
  },
  exigemValor: ["ORCAMENTO_ENVIADO", "FECHADO"],
};

export const funilPadrao = (): Funil => Funil.doMapa(MAPA_DA_API);

export const HOJE = "2026-09-15";
export const VALOR = ValorOrcado.deTexto("4200");

export function orcamento(
  estagio: Estagio = "NOVO_CONTATO",
  extras: Partial<ConstructorParameters<typeof Orcamento>[0]> = {},
): Orcamento {
  return new Orcamento({
    id: "orc-1",
    clienteId: "cli-1",
    clienteNome: "Maria",
    estagio,
    valor: null,
    dataAbertura: "2026-09-01",
    dataFechamento: null,
    qtdInteracoes: 0,
    ...extras,
  });
}
