from collections.abc import Iterable
from dataclasses import dataclass, replace
from datetime import date, datetime
from uuid import UUID, uuid4

from domain.entities.orcamento import Orcamento
from domain.exceptions import FormatoInvalido, OperacaoNaoPermitida
from domain.value_objects.email import Email
from domain.value_objects.telefone import Telefone


@dataclass(frozen=True, kw_only=True)
class Cliente:
    """Aggregate root de contato. Ligado aos seus Orçamentos apenas por `cliente_id`.

    Telefone e e-mail são Value Objects: um Cliente com contato inválido não
    chega a existir (RF09). Imutável: alterações devolvem um novo Cliente.
    """

    id: UUID
    nome: str
    telefone: Telefone
    email: Email
    criado_em: datetime
    empresa: str | None = None
    tipo_embalagem_interesse: str | None = None

    def __post_init__(self) -> None:
        nome = self.nome.strip()
        if not nome:
            raise FormatoInvalido("O nome do cliente é obrigatório.", campo="nome")
        object.__setattr__(self, "nome", nome)

    @classmethod
    def cadastrar(
        cls,
        *,
        nome: str,
        telefone: Telefone,
        email: Email,
        agora: datetime,
        empresa: str | None = None,
        tipo_embalagem_interesse: str | None = None,
    ) -> "Cliente":
        return cls(
            id=uuid4(),
            nome=nome,
            telefone=telefone,
            email=email,
            criado_em=agora,
            empresa=empresa,
            tipo_embalagem_interesse=tipo_embalagem_interesse,
        )

    def abrir_orcamento(self, hoje: date) -> Orcamento:
        """Abre um novo Orçamento em NOVO_CONTATO para este cliente (RF01, RF08)."""
        return Orcamento.abrir(cliente_id=self.id, hoje=hoje)

    def reabrir_atendimento(self, orcamentos: Iterable[Orcamento], hoje: date) -> Orcamento:
        """Traz o cliente de volta ao funil com um novo Orçamento em NOVO_CONTATO.

        Os orçamentos encerrados ficam como estão: Perdido continua terminal (RN01)
        e segue contando na taxa de fechamento. Só faz sentido se nenhum estiver em aberto.
        """
        if any(o.esta_em_aberto() for o in orcamentos):
            raise OperacaoNaoPermitida(f"{self.nome} já tem um orçamento em aberto.")
        return self.abrir_orcamento(hoje)

    def atualizar_contato(self, *, telefone: Telefone, email: Email) -> "Cliente":
        return replace(self, telefone=telefone, email=email)
