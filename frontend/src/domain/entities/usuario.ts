import type { ResultadoValidacao, ErrosPorCampo } from "@/domain/entities/novo-contato";
import { ErroDominio, FormatoInvalido } from "@/domain/errors";
import { Email } from "@/domain/value-objects/email";

export const TAMANHO_MINIMO_DA_SENHA = 8;

export const PERFIS = ["USUARIO", "ADMINISTRADOR"] as const;

export type Perfil = (typeof PERFIS)[number];

export interface DadosUsuario {
  id: string;
  nome: string;
  email: string;
  perfil: Perfil;
  ativo: boolean;
}

/** Operador do sistema. O perfil define o que ele pode fazer (RF10, RNF07). */
export class Usuario implements DadosUsuario {
  readonly id: string;
  readonly nome: string;
  readonly email: string;
  readonly perfil: Perfil;
  readonly ativo: boolean;

  constructor(dados: DadosUsuario) {
    const nome = dados.nome.trim();
    if (!nome) throw new FormatoInvalido("O nome do usuário é obrigatório.", "nome");
    this.id = dados.id;
    this.nome = nome;
    this.email = dados.email;
    this.perfil = dados.perfil;
    this.ativo = dados.ativo;
    Object.freeze(this);
  }

  podeGerenciarUsuarios(): boolean {
    return this.ativo && this.perfil === "ADMINISTRADOR";
  }

  /** Ativar, desativar ou mudar perfil: só admin, e nunca na própria conta. */
  podeAlterarStatusDe(outro: Usuario): boolean {
    return this.podeGerenciarUsuarios() && outro.id !== this.id;
  }
}

export interface EntradaNovoUsuario {
  nome: string;
  email: string;
  senha: string;
  perfil: Perfil;
}

/** Validação do formulário de novo usuário: todos os erros de uma vez. */
export const NovoUsuario = {
  validar(entrada: EntradaNovoUsuario): ResultadoValidacao<EntradaNovoUsuario> {
    const erros: ErrosPorCampo = {};
    const nome = entrada.nome.trim();
    if (!nome) erros.nome = "O nome do usuário é obrigatório.";
    let email = "";
    try {
      email = Email.criar(entrada.email).endereco;
    } catch (erro) {
      if (!(erro instanceof ErroDominio)) throw erro;
      erros.email = erro.mensagem;
    }
    if (entrada.senha.length < TAMANHO_MINIMO_DA_SENHA) {
      erros.senha = `A senha precisa ter pelo menos ${TAMANHO_MINIMO_DA_SENHA} caracteres.`;
    }
    if (Object.keys(erros).length > 0) return { ok: false, erros };
    return { ok: true, valor: { ...entrada, nome, email } };
  },
};
