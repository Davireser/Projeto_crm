/** Formato JSON da API (camelCase). Espelha os schemas Pydantic do backend (RNF05). */
import type { Perfil } from "@/domain/entities/usuario";
import type { Estagio } from "@/domain/value-objects/estagio-atendimento";
import type { TipoInteracao } from "@/domain/value-objects/tipo-interacao";

/** Decimal serializado como texto, ex.: `"4200.00"`. */
type DecimalTexto = string;

export interface CardDto {
  id: string;
  clienteId: string;
  clienteNome: string;
  estagio: Estagio;
  valor: DecimalTexto | null;
  dataAbertura: string;
  dataFechamento?: string | null;
  qtdInteracoes: number;
}

export interface OrcamentoDto {
  id: string;
  clienteId: string;
  estagio: Estagio;
  valor: DecimalTexto | null;
  dataAbertura: string;
  dataFechamento: string | null;
}

export interface ClienteDto {
  id: string;
  nome: string;
  telefone: string;
  email: string;
  empresa: string | null;
  tipoEmbalagemInteresse: string | null;
  criadoEm: string;
}

export interface ClienteDetalheDto extends ClienteDto {
  orcamentos: OrcamentoDto[];
}

export interface ContatoRegistradoDto {
  cliente: ClienteDto;
  orcamento: OrcamentoDto;
}

export interface InteracaoDto {
  id: string;
  tipo: TipoInteracao;
  conteudo: string;
  dataHora: string;
}

export interface ItemHistoricoDto extends InteracaoDto {
  orcamentoId: string;
}

export interface MetricasDto {
  emAberto: number;
  fechados: number;
  perdidos: number;
  taxaFechamento: DecimalTexto | null;
}

export interface UsuarioDto {
  id: string;
  nome: string;
  email: string;
  perfil: Perfil;
  ativo: boolean;
}

export interface TokenDto {
  accessToken: string;
  tokenType: "bearer";
  expiraEm: string;
  usuario: UsuarioDto;
}
