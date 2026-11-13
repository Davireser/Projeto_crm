import { ValorInvalido } from "@/domain/errors";

// Aceita "4200", "4200.50", "4.200,50", "12.500" e "R$ 1.234,56". Guarda em centavos
// inteiros para não sofrer com arredondamento de ponto flutuante.
const PREFIXO_MOEDA = /^R\$\s*/i;
const FORMATO_BR = /^\d{1,3}(?:\.\d{3})*(?:,\d+)?$|^\d+(?:,\d+)?$/;
// No máximo duas casas: "12.500" (três dígitos após o ponto) é milhar no formato brasileiro.
const FORMATO_API = /^\d+(?:\.\d{1,2})?$/;

const REAIS = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });
const DECIMAL_BR = new Intl.NumberFormat("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

/** `R$ 4.200,50`; aceita zero (somas de estágios vazios), ao contrário de um ValorOrcado. */
export const formatarCentavos = (centavos: number): string => REAIS.format(centavos / 100);

/** `"4200.50"` (decimal da API) em centavos inteiros. */
export const centavosDoDecimal = (decimal: string): number => Math.round(Number(decimal) * 100);

/** Valor em BRL, maior que zero, com no máximo duas casas decimais (RN06). */
export class ValorOrcado {
  private constructor(readonly centavos: number) {
    Object.freeze(this);
  }

  static deCentavos(centavos: number): ValorOrcado {
    if (!Number.isSafeInteger(centavos) || centavos <= 0) {
      throw new ValorInvalido(`Valor orçado deve ser maior que zero; recebido ${centavos / 100}.`, "valor");
    }
    return new ValorOrcado(centavos);
  }

  /** Lê o texto digitado pelo usuário ou o decimal vindo da API. */
  static deTexto(texto: string): ValorOrcado {
    const limpo = texto.trim().replace(PREFIXO_MOEDA, "");
    let inteiro: string;
    let fracao: string;
    if (FORMATO_API.test(limpo)) {
      [inteiro = "", fracao = ""] = limpo.split(".");
    } else if (FORMATO_BR.test(limpo)) {
      [inteiro = "", fracao = ""] = limpo.replaceAll(".", "").split(",");
    } else {
      throw new ValorInvalido(`Valor orçado inválido: '${texto}'.`, "valor");
    }
    if (fracao.length > 2) {
      throw new ValorInvalido(
        `Valor orçado aceita no máximo duas casas decimais; recebido ${texto}.`,
        "valor",
      );
    }
    return ValorOrcado.deCentavos(Number(inteiro) * 100 + Number(fracao.padEnd(2, "0")));
  }

  /** Decimal com duas casas, no formato que a API espera: `"4200.50"`. */
  paraApi(): string {
    const reais = Math.trunc(this.centavos / 100);
    const centavos = String(this.centavos % 100).padStart(2, "0");
    return `${reais}.${centavos}`;
  }

  /** `4.200,50`: como o usuário digitaria; `deTexto` lê de volta. */
  paraEdicao(): string {
    return DECIMAL_BR.format(this.centavos / 100);
  }

  /** `R$ 4.200,50`. */
  formatado(): string {
    return formatarCentavos(this.centavos);
  }

  igualA(outro: ValorOrcado): boolean {
    return this.centavos === outro.centavos;
  }
}
