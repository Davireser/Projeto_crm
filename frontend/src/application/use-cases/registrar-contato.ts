import { ErroDeValidacao } from "@/application/errors";
import type { ClienteGateway, ContatoRegistrado } from "@/application/ports";
import { NovoContato, type EntradaNovoContato } from "@/domain/entities/novo-contato";

/** UC01: cadastra o cliente com o primeiro orçamento em Novo contato (RF01, RF09). */
export class RegistrarContato {
  constructor(private readonly clientes: ClienteGateway) {}

  async executar(entrada: EntradaNovoContato): Promise<ContatoRegistrado> {
    const resultado = NovoContato.validar(entrada);
    if (!resultado.ok) throw new ErroDeValidacao(resultado.erros);
    return this.clientes.registrarContato(resultado.valor);
  }
}
