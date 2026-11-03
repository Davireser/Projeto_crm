import { FormatoInvalido } from "@/domain/errors";
import { ESTAGIOS, EstagioAtendimento, type Estagio } from "@/domain/value-objects/estagio-atendimento";

/** JSON de `GET /orcamentos/transicoes`: a fonte única das regras do funil é o backend. */
export interface MapaDeTransicoes {
  transicoes: Partial<Record<string, readonly string[]>>;
  exigemValor: readonly string[];
}

/**
 * Regras de movimento do funil (RN01, RN02), montadas a partir do mapa da API.
 * O frontend não reescreve a tabela de transições: só a valida e a consulta.
 */
export class Funil {
  private constructor(
    private readonly destinos: ReadonlyMap<Estagio, readonly Estagio[]>,
    private readonly comValorObrigatorio: ReadonlySet<Estagio>,
  ) {
    Object.freeze(this);
  }

  static doMapa(mapa: MapaDeTransicoes): Funil {
    const destinos = new Map<Estagio, readonly Estagio[]>();
    for (const origem of ESTAGIOS) {
      const lista = mapa.transicoes[origem];
      if (lista === undefined) {
        throw new FormatoInvalido(`Mapa de transições sem o estágio ${origem}.`, "transicoes");
      }
      destinos.set(origem, lista.map(estagioConhecido));
    }
    return new Funil(destinos, new Set(mapa.exigemValor.map(estagioConhecido)));
  }

  destinosDe(origem: Estagio): readonly Estagio[] {
    return this.destinos.get(origem) ?? [];
  }

  podeMover(origem: Estagio, destino: Estagio): boolean {
    return this.destinosDe(origem).includes(destino);
  }

  ehTerminal(estagio: Estagio): boolean {
    return this.destinosDe(estagio).length === 0;
  }

  exigeValor(estagio: Estagio): boolean {
    return this.comValorObrigatorio.has(estagio);
  }
}

function estagioConhecido(valor: string): Estagio {
  if (!EstagioAtendimento.eh(valor)) {
    throw new FormatoInvalido(`Estágio desconhecido no mapa de transições: ${valor}.`, "transicoes");
  }
  return valor;
}
