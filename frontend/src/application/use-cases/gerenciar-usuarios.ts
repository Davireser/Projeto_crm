import { AcessoNegado, ErroDeValidacao } from "@/application/errors";
import type { AlteracaoUsuario, UsuarioGateway } from "@/application/ports";
import {
  EdicaoUsuario,
  NovoUsuario,
  type EntradaNovoUsuario,
  type Usuario,
} from "@/domain/entities/usuario";
import { OperacaoNaoPermitida } from "@/domain/errors";

/**
 * UC10: só administrador ativo gerencia usuários, e nunca a própria conta
 * (RF10, RNF07). O backend repete as mesmas checagens.
 */
export class GerenciarUsuarios {
  constructor(private readonly usuarios: UsuarioGateway) {}

  async listar(solicitante: Usuario): Promise<Usuario[]> {
    exigirAdministrador(solicitante);
    return this.usuarios.listar();
  }

  async criar(solicitante: Usuario, entrada: EntradaNovoUsuario): Promise<Usuario> {
    exigirAdministrador(solicitante);
    const resultado = NovoUsuario.validar(entrada);
    if (!resultado.ok) throw new ErroDeValidacao(resultado.erros);
    return this.usuarios.criar(resultado.valor);
  }

  async alterar(solicitante: Usuario, alvo: Usuario, alteracao: AlteracaoUsuario): Promise<Usuario> {
    exigirAdministrador(solicitante);
    if (!solicitante.podeAlterarStatusDe(alvo)) {
      throw new OperacaoNaoPermitida("Um administrador não pode alterar a própria conta.", "ativo");
    }
    const { nome, email, ...resto } = alteracao;
    const edicao = EdicaoUsuario.validar({ nome, email });
    if (!edicao.ok) throw new ErroDeValidacao(edicao.erros);
    return this.usuarios.alterar(alvo.id, { ...resto, ...edicao.valor });
  }
}

function exigirAdministrador(solicitante: Usuario): void {
  if (!solicitante.podeGerenciarUsuarios()) throw new AcessoNegado();
}
