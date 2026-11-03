import { FormatoInvalido } from "@/domain/errors";

const CARACTERES_DE_MASCARA = /[\s().+-]/g;
// DDD: dois dígitos de 1 a 9. Fixo: 8 dígitos. Celular: 9 dígitos começando com 9.
const TELEFONE_BRASILEIRO = /^[1-9]{2}(?:[2-8]\d{7}|9\d{8})$/;

/** Telefone brasileiro com DDD, guardado só com dígitos (RN04). */
export class Telefone {
  private constructor(readonly numero: string) {
    Object.freeze(this);
  }

  static criar(texto: string): Telefone {
    const digitos = texto.replace(CARACTERES_DE_MASCARA, "");
    if (!TELEFONE_BRASILEIRO.test(digitos)) {
      throw new FormatoInvalido(
        `Telefone inválido: '${texto}'. Informe DDD + número, ` +
          "com 10 dígitos (fixo) ou 11 dígitos (celular).",
        "telefone",
      );
    }
    return new Telefone(digitos);
  }

  /** `(31) 99876-5432` ou `(11) 3456-7890`. */
  formatado(): string {
    const ddd = this.numero.slice(0, 2);
    const resto = this.numero.slice(2);
    const corte = resto.length - 4;
    return `(${ddd}) ${resto.slice(0, corte)}-${resto.slice(corte)}`;
  }
}
