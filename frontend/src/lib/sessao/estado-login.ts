/** Estado do formulário de login entre o envio e a resposta da Server Action. */
export interface EstadoLogin {
  erro: string | null;
  /** E-mail digitado, para não obrigar a digitar de novo depois de um erro. */
  email: string;
}

export const ESTADO_INICIAL_LOGIN: EstadoLogin = { erro: null, email: "" };
