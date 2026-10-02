from collections.abc import Iterable
from datetime import date, datetime
from uuid import UUID, uuid4

from domain.entities.interacao import Interacao
from domain.exceptions import FormatoInvalido, TransicaoInvalida
from domain.value_objects.estagio_atendimento import EstagioAtendimento
from domain.value_objects.tipo_interacao import TipoInteracao
from domain.value_objects.valor_orcado import ValorOrcado


class Orcamento:
    """Aggregate root do funil — dono das regras de transição de estágio.

    O construtor serve à reconstituição pelo repositório; um orçamento novo
    nasce por `Orcamento.abrir()` ou `Cliente.abrir_orcamento()`.
    """

    def __init__(
        self,
        *,
        id: UUID,
        cliente_id: UUID,
        estagio: EstagioAtendimento,
        valor: ValorOrcado | None,
        data_abertura: date,
        data_fechamento: date | None = None,
        interacoes: Iterable[Interacao] = (),
    ) -> None:
        self._id = id
        self._cliente_id = cliente_id
        self._estagio = estagio
        self._valor = valor
        self._data_abertura = data_abertura
        self._data_fechamento = data_fechamento
        self._interacoes = list(interacoes)

    @classmethod
    def abrir(cls, cliente_id: UUID, hoje: date) -> "Orcamento":
        return cls(
            id=uuid4(),
            cliente_id=cliente_id,
            estagio=EstagioAtendimento.NOVO_CONTATO,
            valor=None,
            data_abertura=hoje,
        )

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def cliente_id(self) -> UUID:
        return self._cliente_id

    @property
    def estagio(self) -> EstagioAtendimento:
        return self._estagio

    @property
    def valor(self) -> ValorOrcado | None:
        return self._valor

    @property
    def data_abertura(self) -> date:
        return self._data_abertura

    @property
    def data_fechamento(self) -> date | None:
        return self._data_fechamento

    @property
    def interacoes(self) -> tuple[Interacao, ...]:
        return tuple(self._interacoes)

    def esta_em_aberto(self) -> bool:
        return not self._estagio.eh_terminal()

    def mover_estagio(self, novo_estagio: EstagioAtendimento, hoje: date) -> None:
        """Aplica RN01 (sequência), RN02 (guarda de valor) e RN03 (data de fechamento).

        Todas as validações acontecem antes de qualquer alteração de estado.
        """
        if not self._estagio.pode_mover_para(novo_estagio):
            raise TransicaoInvalida(
                f"Não é possível mover de {self._estagio} para {novo_estagio}",
                campo="estagio",
            )
        if novo_estagio.exige_valor() and self._valor is None:
            raise TransicaoInvalida(
                f"Orçamento sem valor definido não pode ir para {novo_estagio}",
                campo="valor",
            )

        self._estagio = novo_estagio
        if novo_estagio.eh_terminal():
            self._data_fechamento = hoje

    def definir_valor(self, valor: ValorOrcado) -> None:
        if not self.esta_em_aberto():
            raise TransicaoInvalida(
                f"Orçamento em {self._estagio} está encerrado e não pode ter o valor alterado",
                campo="valor",
            )
        self._valor = valor

    def registrar_interacao(self, tipo: TipoInteracao, conteudo: str, agora: datetime) -> Interacao:
        conteudo = conteudo.strip()
        if not conteudo:
            raise FormatoInvalido("O conteúdo da interação é obrigatório.", campo="conteudo")

        interacao = Interacao(id=uuid4(), tipo=tipo, conteudo=conteudo, data_hora=agora)
        self._interacoes.append(interacao)
        return interacao
