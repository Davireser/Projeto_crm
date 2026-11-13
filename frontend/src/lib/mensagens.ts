import { ErroDeValidacao, ErroRemoto } from "@/application/errors";
import type { ErrosPorCampo } from "@/domain/entities/novo-contato";
import { ErroDominio } from "@/domain/errors";

/** Texto para mostrar ao usuário: a mensagem do domínio ou da API, nunca um stack trace. */
export function mensagemDeErro(erro: unknown): string {
  if (erro instanceof ErroDominio || erro instanceof ErroRemoto) return erro.mensagem;
  return "Algo deu errado. Tente de novo.";
}

/** Erros de um formulário por campo; o que não tem campo vai para `geral`. */
export function errosDoFormulario(erro: unknown): ErrosPorCampo {
  if (erro instanceof ErroDeValidacao) return erro.erros;
  if (erro instanceof ErroRemoto && erro.campo) return { [erro.campo]: erro.mensagem };
  return { geral: mensagemDeErro(erro) };
}
