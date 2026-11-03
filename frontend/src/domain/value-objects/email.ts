import { FormatoInvalido } from "@/domain/errors";

const EMAIL = /^[a-z0-9._%+-]+@[a-z0-9-]+(?:\.[a-z0-9-]+)*\.[a-z]{2,}$/;

/** Endereço `local@dominio.tld`, normalizado para minúsculas (RN05). */
export class Email {
  private constructor(readonly endereco: string) {
    Object.freeze(this);
  }

  static criar(texto: string): Email {
    const normalizado = texto.trim().toLowerCase();
    if (!EMAIL.test(normalizado)) {
      throw new FormatoInvalido(`E-mail inválido: '${texto}'.`, "email");
    }
    return new Email(normalizado);
  }

  igualA(outro: Email): boolean {
    return this.endereco === outro.endereco;
  }
}
