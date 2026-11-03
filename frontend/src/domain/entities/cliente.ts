import type { Email } from "@/domain/value-objects/email";
import type { Telefone } from "@/domain/value-objects/telefone";

export interface DadosCliente {
  id: string;
  nome: string;
  telefone: Telefone;
  email: Email;
  empresa: string | null;
  tipoEmbalagemInteresse: string | null;
  /** Instante ISO 8601 em UTC. */
  criadoEm: string;
}

/** Cliente com contato já validado (telefone e e-mail são Value Objects, RF09). */
export class Cliente implements DadosCliente {
  readonly id: string;
  readonly nome: string;
  readonly telefone: Telefone;
  readonly email: Email;
  readonly empresa: string | null;
  readonly tipoEmbalagemInteresse: string | null;
  readonly criadoEm: string;

  constructor(dados: DadosCliente) {
    this.id = dados.id;
    this.nome = dados.nome;
    this.telefone = dados.telefone;
    this.email = dados.email;
    this.empresa = dados.empresa;
    this.tipoEmbalagemInteresse = dados.tipoEmbalagemInteresse;
    this.criadoEm = dados.criadoEm;
    Object.freeze(this);
  }
}
