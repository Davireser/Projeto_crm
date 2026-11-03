import type { ErrosPorCampo } from "@/domain/entities/novo-contato";

/** Formulário com um ou mais campos inválidos; a API nem é chamada. */
export class ErroDeValidacao extends Error {
  constructor(readonly erros: ErrosPorCampo) {
    super("Há campos inválidos no formulário.");
    this.name = "ErroDeValidacao";
  }
}

/** Usuário sem permissão para a operação (RNF07). */
export class AcessoNegado extends Error {
  constructor(mensagem = "Você não tem permissão para esta operação.") {
    super(mensagem);
    this.name = "AcessoNegado";
  }
}

/**
 * Erro devolvido pela API no formato `{erro, mensagem, campo}`, ou falha de rede
 * (`status` 0). As portas lançam este erro; a interface mostra a `mensagem`.
 */
export class ErroRemoto extends Error {
  constructor(
    readonly status: number,
    readonly codigo: string,
    readonly mensagem: string,
    readonly campo: string | null = null,
  ) {
    super(mensagem);
    this.name = "ErroRemoto";
  }

  get sessaoExpirada(): boolean {
    return this.status === 401;
  }

  get semConexao(): boolean {
    return this.status === 0;
  }
}
