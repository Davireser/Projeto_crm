/**
 * Erros de domínio. Espelham as exceções do backend: cada um carrega a
 * `mensagem` exibida ao usuário e o `campo` do formulário a que se refere.
 */
export class ErroDominio extends Error {
  readonly mensagem: string;
  readonly campo: string | null;

  constructor(mensagem: string, campo: string | null = null) {
    super(mensagem);
    this.name = new.target.name;
    this.mensagem = mensagem;
    this.campo = campo;
  }
}

/** Par origem→destino fora do funil ou guarda de valor violada (RF02, RF03). */
export class TransicaoInvalida extends ErroDominio {}

/** Dado em formato inválido — telefone, e-mail, nome, conteúdo (RF09). */
export class FormatoInvalido extends ErroDominio {}

/** Valor orçado zero, negativo ou com mais de duas casas decimais (RN06). */
export class ValorInvalido extends ErroDominio {}

/** Operação proibida pela regra de negócio, como a auto-desativação (RF10). */
export class OperacaoNaoPermitida extends ErroDominio {}
