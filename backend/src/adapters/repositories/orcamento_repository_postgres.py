from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from domain.entities.interacao import Interacao
from domain.entities.orcamento import Orcamento
from domain.repositories.orcamento_repository import OrcamentoRepository
from domain.value_objects.estagio_atendimento import EstagioAtendimento
from domain.value_objects.tipo_interacao import TipoInteracao
from domain.value_objects.valor_orcado import ValorOrcado
from infra.db.models import InteracaoModel, OrcamentoModel


class OrcamentoRepositoryPostgres(OrcamentoRepository):
    """Persiste o agregado Orcamento (com suas Interações) via SQLAlchemy.

    Escrito em SQLAlchemy portável: roda no PostgreSQL em produção e no SQLite
    nos testes. Não faz commit — a transação pertence à requisição.
    """

    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def salvar(self, orcamento: Orcamento) -> None:
        model = self._sessao.get(OrcamentoModel, orcamento.id)
        if model is None:
            model = OrcamentoModel(id=orcamento.id)
            self._sessao.add(model)

        model.cliente_id = orcamento.cliente_id
        model.estagio = orcamento.estagio.value
        model.valor = orcamento.valor.valor if orcamento.valor else None
        model.data_abertura = orcamento.data_abertura
        model.data_fechamento = orcamento.data_fechamento

        # Interações são imutáveis e só crescem: basta acrescentar as novas.
        ja_gravadas = {i.id for i in model.interacoes}
        for interacao in orcamento.interacoes:
            if interacao.id not in ja_gravadas:
                model.interacoes.append(
                    InteracaoModel(
                        id=interacao.id,
                        tipo=interacao.tipo.value,
                        conteudo=interacao.conteudo,
                        data_hora=interacao.data_hora,
                    )
                )
        self._sessao.flush()

    def buscar_por_id(self, orcamento_id: UUID) -> Orcamento | None:
        model = self._sessao.get(OrcamentoModel, orcamento_id)
        return _para_entidade(model) if model else None

    def listar_todos(self) -> list[Orcamento]:
        consulta = select(OrcamentoModel).order_by(OrcamentoModel.data_abertura)
        return [_para_entidade(m) for m in self._sessao.scalars(consulta)]

    def listar_por_cliente(self, cliente_id: UUID) -> list[Orcamento]:
        consulta = (
            select(OrcamentoModel)
            .where(OrcamentoModel.cliente_id == cliente_id)
            .order_by(OrcamentoModel.data_abertura)
        )
        return [_para_entidade(m) for m in self._sessao.scalars(consulta)]


def _para_entidade(model: OrcamentoModel) -> Orcamento:
    return Orcamento(
        id=model.id,
        cliente_id=model.cliente_id,
        estagio=EstagioAtendimento(model.estagio),
        valor=ValorOrcado(model.valor) if model.valor is not None else None,
        data_abertura=model.data_abertura,
        data_fechamento=model.data_fechamento,
        interacoes=[
            Interacao(
                id=i.id, tipo=TipoInteracao(i.tipo), conteudo=i.conteudo, data_hora=i.data_hora
            )
            for i in model.interacoes
        ],
    )
