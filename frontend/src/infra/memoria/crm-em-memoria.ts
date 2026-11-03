/**
 * Gateways em memória: implementam as mesmas portas do HTTP, sem rede.
 * Usados nos testes dos casos de uso e da interface.
 */
import type {
  AlteracaoUsuario,
  AtualizacaoOrcamento,
  ClienteComOrcamentos,
  ClienteGateway,
  ContatoRegistrado,
  ItemHistorico,
  MetricasGateway,
  OrcamentoGateway,
  UsuarioGateway,
} from "@/application/ports";
import { Cliente } from "@/domain/entities/cliente";
import { Interacao } from "@/domain/entities/interacao";
import { MetricasFunil } from "@/domain/entities/metricas-funil";
import type { NovoContatoValido } from "@/domain/entities/novo-contato";
import { Orcamento } from "@/domain/entities/orcamento";
import { Usuario, type EntradaNovoUsuario } from "@/domain/entities/usuario";
import { Funil, type MapaDeTransicoes } from "@/domain/funil/funil";
import type { Estagio } from "@/domain/value-objects/estagio-atendimento";
import type { TipoInteracao } from "@/domain/value-objects/tipo-interacao";
import type { ValorOrcado } from "@/domain/value-objects/valor-orcado";

type Relogio = () => Date;

export class CrmEmMemoria {
  readonly clientesSalvos = new Map<string, Cliente>();
  readonly orcamentosSalvos = new Map<string, Orcamento>();
  readonly historicoSalvo: ItemHistorico[] = [];
  readonly orcamentos: OrcamentosEmMemoria;
  readonly clientes: ClientesEmMemoria;
  readonly metricas: MetricasEmMemoria;
  private proximoId = 1;

  constructor(
    readonly mapa: MapaDeTransicoes,
    readonly relogio: Relogio = () => new Date(),
  ) {
    this.orcamentos = new OrcamentosEmMemoria(this);
    this.clientes = new ClientesEmMemoria(this);
    this.metricas = new MetricasEmMemoria(this);
  }

  novoId(prefixo: string): string {
    return `${prefixo}-${this.proximoId++}`;
  }

  hoje(): string {
    return this.relogio().toISOString().slice(0, 10);
  }

  orcamento(id: string): Orcamento {
    const orcamento = this.orcamentosSalvos.get(id);
    if (!orcamento) throw new Error(`Orçamento ${id} não encontrado`);
    return orcamento;
  }
}

export class OrcamentosEmMemoria implements OrcamentoGateway {
  /** Escritas recebidas, para os testes conferirem o que chegou na "API". */
  readonly chamadas: string[] = [];

  constructor(private readonly crm: CrmEmMemoria) {}

  async listarCards(): Promise<Orcamento[]> {
    return [...this.crm.orcamentosSalvos.values()];
  }

  async obterTransicoes(): Promise<MapaDeTransicoes> {
    return this.crm.mapa;
  }

  async moverEstagio(id: string, destino: Estagio): Promise<AtualizacaoOrcamento> {
    this.chamadas.push(`mover ${id} ${destino}`);
    const movido = this.crm.orcamento(id).moverPara(destino, Funil.doMapa(this.crm.mapa), this.crm.hoje());
    return this.salvar(movido);
  }

  async definirValor(id: string, valor: ValorOrcado): Promise<AtualizacaoOrcamento> {
    this.chamadas.push(`valor ${id} ${valor.paraApi()}`);
    return this.salvar(this.crm.orcamento(id).definirValor(valor, Funil.doMapa(this.crm.mapa)));
  }

  async registrarInteracao(id: string, tipo: TipoInteracao, conteudo: string): Promise<Interacao> {
    this.chamadas.push(`interacao ${id}`);
    const interacao = new Interacao({
      id: this.crm.novoId("int"),
      tipo,
      conteudo,
      dataHora: this.crm.relogio().toISOString(),
    });
    this.salvar(this.crm.orcamento(id).comNovaInteracao());
    this.crm.historicoSalvo.push({ orcamentoId: id, interacao });
    return interacao;
  }

  private salvar(orcamento: Orcamento): AtualizacaoOrcamento {
    this.crm.orcamentosSalvos.set(orcamento.id, orcamento);
    return { estagio: orcamento.estagio, valor: orcamento.valor, dataFechamento: orcamento.dataFechamento };
  }
}

export class ClientesEmMemoria implements ClienteGateway {
  constructor(private readonly crm: CrmEmMemoria) {}

  async registrarContato(contato: NovoContatoValido): Promise<ContatoRegistrado> {
    const cliente = new Cliente({
      ...contato,
      id: this.crm.novoId("cli"),
      criadoEm: this.crm.relogio().toISOString(),
    });
    const orcamento = new Orcamento({
      id: this.crm.novoId("orc"),
      clienteId: cliente.id,
      clienteNome: cliente.nome,
      estagio: "NOVO_CONTATO",
      valor: null,
      dataAbertura: this.crm.hoje(),
      dataFechamento: null,
      qtdInteracoes: 0,
    });
    this.crm.clientesSalvos.set(cliente.id, cliente);
    this.crm.orcamentosSalvos.set(orcamento.id, orcamento);
    return { clienteId: cliente.id, orcamento };
  }

  async obterCliente(id: string): Promise<ClienteComOrcamentos> {
    const cliente = this.crm.clientesSalvos.get(id);
    if (!cliente) throw new Error(`Cliente ${id} não encontrado`);
    const orcamentos = [...this.crm.orcamentosSalvos.values()]
      .filter((o) => o.clienteId === id)
      .map((o) => new Orcamento({ ...o, qtdInteracoes: 0 }));
    return { cliente, orcamentos };
  }

  async historico(id: string): Promise<ItemHistorico[]> {
    return this.crm.historicoSalvo.filter(
      (item) => this.crm.orcamento(item.orcamentoId).clienteId === id,
    );
  }
}

export class MetricasEmMemoria implements MetricasGateway {
  constructor(private readonly crm: CrmEmMemoria) {}

  async obter(): Promise<MetricasFunil> {
    const estagios = [...this.crm.orcamentosSalvos.values()].map((o) => o.estagio);
    const fechados = estagios.filter((e) => e === "FECHADO").length;
    const perdidos = estagios.filter((e) => e === "PERDIDO").length;
    const concluidos = fechados + perdidos;
    return new MetricasFunil({
      emAberto: estagios.length - concluidos,
      fechados,
      perdidos,
      taxaFechamento: concluidos ? Math.round((10000 * fechados) / concluidos) / 100 : null,
    });
  }
}

export class UsuariosEmMemoria implements UsuarioGateway {
  private readonly usuarios = new Map<string, Usuario>();
  private proximoId = 1;

  constructor(iniciais: Usuario[] = []) {
    for (const usuario of iniciais) this.usuarios.set(usuario.id, usuario);
  }

  async listar(): Promise<Usuario[]> {
    return [...this.usuarios.values()];
  }

  async criar(entrada: EntradaNovoUsuario): Promise<Usuario> {
    const usuario = new Usuario({
      id: `novo-${this.proximoId++}`,
      nome: entrada.nome,
      email: entrada.email,
      perfil: entrada.perfil,
      ativo: true,
    });
    this.usuarios.set(usuario.id, usuario);
    return usuario;
  }

  async alterar(id: string, alteracao: AlteracaoUsuario): Promise<Usuario> {
    const atual = this.usuarios.get(id);
    if (!atual) throw new Error(`Usuário ${id} não encontrado`);
    const alterado = new Usuario({ ...atual, ...alteracao });
    this.usuarios.set(id, alterado);
    return alterado;
  }
}
