/**
 * Portas: o que os casos de uso precisam do mundo externo. A camada infra
 * implementa com HTTP (produção) e em memória (testes).
 */
import type { Cliente } from "@/domain/entities/cliente";
import type { Interacao } from "@/domain/entities/interacao";
import type { MetricasFunil } from "@/domain/entities/metricas-funil";
import type { NovoContatoValido } from "@/domain/entities/novo-contato";
import type { DadosOrcamento, Orcamento } from "@/domain/entities/orcamento";
import type { EntradaNovoUsuario, Perfil, Usuario } from "@/domain/entities/usuario";
import type { MapaDeTransicoes } from "@/domain/funil/funil";
import type { Estagio } from "@/domain/value-objects/estagio-atendimento";
import type { TipoInteracao } from "@/domain/value-objects/tipo-interacao";
import type { ValorOrcado } from "@/domain/value-objects/valor-orcado";

/** O que a API devolve ao alterar um orçamento (sem nome do cliente nem contagem). */
export type AtualizacaoOrcamento = Pick<DadosOrcamento, "estagio" | "valor" | "dataFechamento">;

export interface OrcamentoGateway {
  listarCards(): Promise<Orcamento[]>;
  obterTransicoes(): Promise<MapaDeTransicoes>;
  moverEstagio(id: string, destino: Estagio): Promise<AtualizacaoOrcamento>;
  definirValor(id: string, valor: ValorOrcado): Promise<AtualizacaoOrcamento>;
  registrarInteracao(id: string, tipo: TipoInteracao, conteudo: string): Promise<Interacao>;
}

export interface ContatoRegistrado {
  clienteId: string;
  orcamento: Orcamento;
}

export interface ClienteComOrcamentos {
  cliente: Cliente;
  orcamentos: Orcamento[];
}

export interface ItemHistorico {
  orcamentoId: string;
  interacao: Interacao;
}

export interface ClienteGateway {
  registrarContato(contato: NovoContatoValido): Promise<ContatoRegistrado>;
  obterCliente(id: string): Promise<ClienteComOrcamentos>;
  historico(id: string): Promise<ItemHistorico[]>;
}

export interface MetricasGateway {
  obter(): Promise<MetricasFunil>;
}

export interface AlteracaoUsuario {
  nome?: string;
  email?: string;
  ativo?: boolean;
  perfil?: Perfil;
}

export interface UsuarioGateway {
  listar(): Promise<Usuario[]>;
  criar(entrada: EntradaNovoUsuario): Promise<Usuario>;
  alterar(id: string, alteracao: AlteracaoUsuario): Promise<Usuario>;
}
