import { ErroDominio, FormatoInvalido } from "@/domain/errors";
import { Email } from "@/domain/value-objects/email";
import { Telefone } from "@/domain/value-objects/telefone";

export interface EntradaNovoContato {
  nome: string;
  telefone: string;
  email: string;
  empresa?: string;
  tipoEmbalagemInteresse?: string;
}

export interface NovoContatoValido {
  nome: string;
  telefone: Telefone;
  email: Email;
  empresa: string | null;
  tipoEmbalagemInteresse: string | null;
}

export type ErrosPorCampo = Partial<Record<string, string>>;

export type ResultadoValidacao<T> = { ok: true; valor: T } | { ok: false; erros: ErrosPorCampo };

/**
 * Cadastro de um cliente com o seu primeiro orçamento (RF01). Valida todos os
 * campos de uma vez para o formulário mostrar todos os erros juntos (RF09).
 */
export const NovoContato = {
  validar(entrada: EntradaNovoContato): ResultadoValidacao<NovoContatoValido> {
    const erros: ErrosPorCampo = {};
    const nome = campo(erros, () => nomeObrigatorio(entrada.nome));
    const telefone = campo(erros, () => Telefone.criar(entrada.telefone));
    const email = campo(erros, () => Email.criar(entrada.email));

    if (nome === null || telefone === null || email === null) return { ok: false, erros };
    return {
      ok: true,
      valor: {
        nome,
        telefone,
        email,
        empresa: opcional(entrada.empresa),
        tipoEmbalagemInteresse: opcional(entrada.tipoEmbalagemInteresse),
      },
    };
  },
};

function nomeObrigatorio(nome: string): string {
  const limpo = nome.trim();
  if (!limpo) throw new FormatoInvalido("O nome do cliente é obrigatório.", "nome");
  return limpo;
}

function opcional(texto: string | undefined): string | null {
  return texto?.trim() || null;
}

function campo<T>(erros: ErrosPorCampo, criar: () => T): T | null {
  try {
    return criar();
  } catch (erro) {
    if (!(erro instanceof ErroDominio)) throw erro;
    erros[erro.campo ?? "geral"] = erro.mensagem;
    return null;
  }
}
