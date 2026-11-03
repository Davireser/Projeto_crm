from dataclasses import dataclass, replace
from datetime import date, datetime
from uuid import UUID, uuid4

from domain.entities.interacao import Interacao
from domain.exceptions import FormatoInvalido, TransicaoInvalida
from domain.value_objects.estagio_atendimento import EstagioAtendimento
from domain.value_objects.tipo_interacao import TipoInteracao
from domain.value_objects.valor_orcado import ValorOrcado


@dataclass(frozen=True, kw_only=True)
class Orcamento:
    """Aggregate root do funil — dono das regras de transição de estágio.

    O construtor serve à reconstituição pelo repositório; um orçamento novo
    nasce por `Orcamento.abrir()` ou `Cliente.abrir_orcamento()`.
    Imutável: cada operação devolve um novo Orcamento, que o caso de uso salva.
    """

    id: UUID
    cliente_id: UUID
    estagio: EstagioAtendimento
    valor: ValorOrcado | None
    data_abertura: date
    data_fechamento: date | None = None
    interacoes: tuple[Interacao, ...] = ()

    @classmethod
    def abrir(cls, cliente_id: UUID, hoje: date) -> "Orcamento":
        return cls(
            id=uuid4(),
            cliente_id=cliente_id,
            estagio=EstagioAtendimento.NOVO_CONTATO,
            valor=None,
            data_abertura=hoje,
        )

    def esta_em_aberto(self) -> bool:
        return not self.estagio.eh_terminal()

    def mover_estagio(self, novo_estagio: EstagioAtendimento, hoje: date) -> "Orcamento":
        """Aplica RN01 (sequência), RN02 (guarda de valor) e RN03 (data de fechamento).

        Todas as validações acontecem antes de criar o novo estado.
        """
        if not self.estagio.pode_mover_para(novo_estagio):
            raise TransicaoInvalida(
                f"Não é possível mover de {self.estagio} para {novo_estagio}",
                campo="estagio",
            )
        if novo_estagio.exige_valor() and self.valor is None:
            raise TransicaoInvalida(
                f"Orçamento sem valor definido não pode ir para {novo_estagio}",
                campo="valor",
            )

        data_fechamento = hoje if novo_estagio.eh_terminal() else self.data_fechamento
        return replace(self, estagio=novo_estagio, data_fechamento=data_fechamento)

    def definir_valor(self, valor: ValorOrcado) -> "Orcamento":
        if not self.esta_em_aberto():
            raise TransicaoInvalida(
                f"Orçamento em {self.estagio} está encerrado e não pode ter o valor alterado",
                campo="valor",
            )
        return replace(self, valor=valor)

    def registrar_interacao(
        self, tipo: TipoInteracao, conteudo: str, agora: datetime
    ) -> tuple["Orcamento", Interacao]:
        """Devolve o orçamento com a nova interação e a própria interação criada."""
        conteudo = conteudo.strip()
        if not conteudo:
            raise FormatoInvalido("O conteúdo da interação é obrigatório.", campo="conteudo")

        interacao = Interacao(id=uuid4(), tipo=tipo, conteudo=conteudo, data_hora=agora)
        return replace(self, interacoes=(*self.interacoes, interacao)), interacao
