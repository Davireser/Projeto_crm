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
import type { Interacao } from "@/domain/entities/interacao";
import type { MetricasFunil } from "@/domain/entities/metricas-funil";
import type { NovoContatoValido } from "@/domain/entities/novo-contato";
import type { Orcamento } from "@/domain/entities/orcamento";
import type { EntradaNovoUsuario, Usuario } from "@/domain/entities/usuario";
import type { MapaDeTransicoes } from "@/domain/funil/funil";
import type { Estagio } from "@/domain/value-objects/estagio-atendimento";
import type { TipoInteracao } from "@/domain/value-objects/tipo-interacao";
import type { ValorOrcado } from "@/domain/value-objects/valor-orcado";

import type { ClienteHttp } from "./cliente-http";
import type {
  CardDto,
  ClienteDetalheDto,
  ContatoRegistradoDto,
  InteracaoDto,
  ItemHistoricoDto,
  MetricasDto,
  OrcamentoDto,
  UsuarioDto,
} from "./dtos";
import {
  paraAtualizacao,
  paraCliente,
  paraInteracao,
  paraItemHistorico,
  paraMetricas,
  paraOrcamento,
  paraOrcamentoDoCliente,
  paraUsuario,
} from "./mapeadores";

export class OrcamentoGatewayHttp implements OrcamentoGateway {
  constructor(private readonly http: ClienteHttp) {}

  async listarCards(): Promise<Orcamento[]> {
    return (await this.http.get<CardDto[]>("/orcamentos")).map(paraOrcamento);
  }

  obterTransicoes(): Promise<MapaDeTransicoes> {
    return this.http.get<MapaDeTransicoes>("/orcamentos/transicoes");
  }

  async moverEstagio(id: string, destino: Estagio): Promise<AtualizacaoOrcamento> {
    return paraAtualizacao(
      await this.http.patch<OrcamentoDto>(`/orcamentos/${id}/estagio`, { estagio: destino }),
    );
  }

  async definirValor(id: string, valor: ValorOrcado): Promise<AtualizacaoOrcamento> {
    return paraAtualizacao(
      await this.http.patch<OrcamentoDto>(`/orcamentos/${id}/valor`, { valor: valor.paraApi() }),
    );
  }

  async registrarInteracao(id: string, tipo: TipoInteracao, conteudo: string): Promise<Interacao> {
    return paraInteracao(
      await this.http.post<InteracaoDto>(`/orcamentos/${id}/interacoes`, { tipo, conteudo }),
    );
  }
}

export class ClienteGatewayHttp implements ClienteGateway {
  constructor(private readonly http: ClienteHttp) {}

  async registrarContato(contato: NovoContatoValido): Promise<ContatoRegistrado> {
    const { cliente, orcamento } = await this.http.post<ContatoRegistradoDto>("/clientes", {
      nome: contato.nome,
      telefone: contato.telefone.numero,
      email: contato.email.endereco,
      empresa: contato.empresa,
      tipoEmbalagemInteresse: contato.tipoEmbalagemInteresse,
    });
    return { clienteId: cliente.id, orcamento: paraOrcamentoDoCliente(orcamento, cliente.nome) };
  }

  async obterCliente(id: string): Promise<ClienteComOrcamentos> {
    const dto = await this.http.get<ClienteDetalheDto>(`/clientes/${id}`);
    return {
      cliente: paraCliente(dto),
      orcamentos: dto.orcamentos.map((o) => paraOrcamentoDoCliente(o, dto.nome)),
    };
  }

  async historico(id: string): Promise<ItemHistorico[]> {
    return (await this.http.get<ItemHistoricoDto[]>(`/clientes/${id}/historico`)).map(
      paraItemHistorico,
    );
  }
}

export class MetricasGatewayHttp implements MetricasGateway {
  constructor(private readonly http: ClienteHttp) {}

  async obter(): Promise<MetricasFunil> {
    return paraMetricas(await this.http.get<MetricasDto>("/metricas/funil"));
  }
}

export class UsuarioGatewayHttp implements UsuarioGateway {
  constructor(private readonly http: ClienteHttp) {}

  async listar(): Promise<Usuario[]> {
    return (await this.http.get<UsuarioDto[]>("/usuarios")).map(paraUsuario);
  }

  async criar(entrada: EntradaNovoUsuario): Promise<Usuario> {
    return paraUsuario(await this.http.post<UsuarioDto>("/usuarios", entrada));
  }

  async alterar(id: string, alteracao: AlteracaoUsuario): Promise<Usuario> {
    return paraUsuario(await this.http.patch<UsuarioDto>(`/usuarios/${id}`, alteracao));
  }
}
