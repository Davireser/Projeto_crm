import type { AtualizacaoOrcamento, ItemHistorico } from "@/application/ports";
import { Cliente } from "@/domain/entities/cliente";
import { Interacao } from "@/domain/entities/interacao";
import { MetricasFunil } from "@/domain/entities/metricas-funil";
import { Orcamento } from "@/domain/entities/orcamento";
import { Usuario } from "@/domain/entities/usuario";
import { Email } from "@/domain/value-objects/email";
import { Telefone } from "@/domain/value-objects/telefone";
import { ValorOrcado, centavosDoDecimal } from "@/domain/value-objects/valor-orcado";

import type {
  CardDto,
  ClienteDto,
  InteracaoDto,
  ItemHistoricoDto,
  MetricasDto,
  OrcamentoDto,
  UsuarioDto,
} from "./dtos";

const valor = (texto: string | null): ValorOrcado | null =>
  texto === null ? null : ValorOrcado.deTexto(texto);

export const paraOrcamento = (dto: CardDto): Orcamento =>
  new Orcamento({
    id: dto.id,
    clienteId: dto.clienteId,
    clienteNome: dto.clienteNome,
    estagio: dto.estagio,
    valor: valor(dto.valor),
    dataAbertura: dto.dataAbertura,
    dataFechamento: dto.dataFechamento ?? null,
    qtdInteracoes: dto.qtdInteracoes,
  });

/** Caminho de volta: o cache offline guarda o JSON da API, não as classes do domínio. */
export const paraCardDto = (orcamento: Orcamento): CardDto => ({
  id: orcamento.id,
  clienteId: orcamento.clienteId,
  clienteNome: orcamento.clienteNome,
  estagio: orcamento.estagio,
  valor: orcamento.valor?.paraApi() ?? null,
  dataAbertura: orcamento.dataAbertura,
  dataFechamento: orcamento.dataFechamento,
  qtdInteracoes: orcamento.qtdInteracoes,
});

export const paraOrcamentoDoCliente =(dto: OrcamentoDto, clienteNome: string): Orcamento =>
  paraOrcamento({ ...dto, clienteNome, qtdInteracoes: 0 });

export const paraAtualizacao = (dto: OrcamentoDto): AtualizacaoOrcamento => ({
  estagio: dto.estagio,
  valor: valor(dto.valor),
  dataFechamento: dto.dataFechamento,
});

export const paraCliente = (dto: ClienteDto): Cliente =>
  new Cliente({
    ...dto,
    telefone: Telefone.criar(dto.telefone),
    email: Email.criar(dto.email),
  });

export const paraInteracao = (dto: InteracaoDto): Interacao =>
  new Interacao({ id: dto.id, tipo: dto.tipo, conteudo: dto.conteudo, dataHora: dto.dataHora });

export const paraItemHistorico = (dto: ItemHistoricoDto): ItemHistorico => ({
  orcamentoId: dto.orcamentoId,
  interacao: paraInteracao(dto),
});

export const paraMetricas = (dto: MetricasDto): MetricasFunil =>
  new MetricasFunil({
    ...dto,
    taxaFechamento: dto.taxaFechamento === null ? null : Number(dto.taxaFechamento),
    porEstagio: dto.porEstagio.map(({ valorTotal, ...total }) => ({
      ...total,
      valorCentavos: centavosDoDecimal(valorTotal),
    })),
  });

export const paraUsuario = (dto: UsuarioDto): Usuario => new Usuario(dto);
