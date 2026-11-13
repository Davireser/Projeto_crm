import { TransicaoInvalida } from "@/domain/errors";
import type { Funil } from "@/domain/funil/funil";
import { rotuloDoEstagio, type Estagio } from "@/domain/value-objects/estagio-atendimento";
import type { ValorOrcado } from "@/domain/value-objects/valor-orcado";

export interface DadosOrcamento {
  id: string;
  clienteId: string;
  clienteNome: string;
  estagio: Estagio;
  valor: ValorOrcado | null;
  /** Data ISO `AAAA-MM-DD`. */
  dataAbertura: string;
  dataFechamento: string | null;
  qtdInteracoes: number;
}

/**
 * Orçamento do funil, como aparece no card do Kanban. Imutável: cada operação
 * devolve um novo Orcamento. As regras são as mesmas do backend (RN01–RN03),
 * o que permite a atualização otimista no arraste (RNF02).
 */
export class Orcamento implements DadosOrcamento {
  readonly id: string;
  readonly clienteId: string;
  readonly clienteNome: string;
  readonly estagio: Estagio;
  readonly valor: ValorOrcado | null;
  readonly dataAbertura: string;
  readonly dataFechamento: string | null;
  readonly qtdInteracoes: number;

  constructor(dados: DadosOrcamento) {
    this.id = dados.id;
    this.clienteId = dados.clienteId;
    this.clienteNome = dados.clienteNome;
    this.estagio = dados.estagio;
    this.valor = dados.valor;
    this.dataAbertura = dados.dataAbertura;
    this.dataFechamento = dados.dataFechamento;
    this.qtdInteracoes = dados.qtdInteracoes;
    Object.freeze(this);
  }

  estaEmAberto(funil: Funil): boolean {
    return !funil.ehTerminal(this.estagio);
  }

  /** Motivo pelo qual o movimento seria recusado, ou `null` se ele é válido. */
  motivoParaNaoMover(destino: Estagio, funil: Funil): string | null {
    try {
      this.validarMovimento(destino, funil);
      return null;
    } catch (erro) {
      if (erro instanceof TransicaoInvalida) return erro.mensagem;
      throw erro;
    }
  }

  moverPara(destino: Estagio, funil: Funil, hoje: string): Orcamento {
    this.validarMovimento(destino, funil);
    return this.com({
      estagio: destino,
      dataFechamento: funil.ehTerminal(destino) ? hoje : this.dataFechamento,
    });
  }

  definirValor(valor: ValorOrcado, funil: Funil): Orcamento {
    if (!this.estaEmAberto(funil)) {
      throw new TransicaoInvalida(
        `Orçamento ${rotuloDoEstagio(this.estagio).toLowerCase()} está encerrado e não pode ter o valor alterado.`,
        "valor",
      );
    }
    return this.com({ valor });
  }

  /**
   * Perdido é terminal (RN01): o cliente volta ao funil com um novo orçamento,
   * e este continua perdido no histórico e na taxa de fechamento.
   */
  podeReabrirAtendimento(): boolean {
    return this.estagio === "PERDIDO";
  }

  comNovaInteracao(): Orcamento {
    return this.com({ qtdInteracoes: this.qtdInteracoes + 1 });
  }

  /** Lança `TransicaoInvalida` se o movimento quebra RN01 ou RN02. */
  validarMovimento(destino: Estagio, funil: Funil): void {
    if (!funil.podeMover(this.estagio, destino)) {
      throw new TransicaoInvalida(
        `Não é possível mover de ${rotuloDoEstagio(this.estagio)} para ${rotuloDoEstagio(destino)}.`,
        "estagio",
      );
    }
    if (funil.exigeValor(destino) && this.valor === null) {
      throw new TransicaoInvalida(
        `Defina o valor do orçamento antes de mover para ${rotuloDoEstagio(destino)}.`,
        "valor",
      );
    }
  }

  private com(mudancas: Partial<DadosOrcamento>): Orcamento {
    return new Orcamento({ ...this, ...mudancas });
  }
}
