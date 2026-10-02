from datetime import date, datetime
from uuid import UUID, uuid4

from domain.entities.orcamento import Orcamento
from domain.exceptions import FormatoInvalido
from domain.value_objects.email import Email
from domain.value_objects.telefone import Telefone


class Cliente:
    """Aggregate root de contato. Ligado aos seus Orçamentos apenas por `cliente_id`.

    Telefone e e-mail são Value Objects: um Cliente com contato inválido não
    chega a existir (RF09).
    """

    def __init__(
        self,
        *,
        id: UUID,
        nome: str,
        telefone: Telefone,
        email: Email,
        criado_em: datetime,
        empresa: str | None = None,
        tipo_embalagem_interesse: str | None = None,
    ) -> None:
        nome = nome.strip()
        if not nome:
            raise FormatoInvalido("O nome do cliente é obrigatório.", campo="nome")

        self._id = id
        self._nome = nome
        self._telefone = telefone
        self._email = email
        self._criado_em = criado_em
        self._empresa = empresa
        self._tipo_embalagem_interesse = tipo_embalagem_interesse

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

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def nome(self) -> str:
        return self._nome

    @property
    def telefone(self) -> Telefone:
        return self._telefone

    @property
    def email(self) -> Email:
        return self._email

    @property
    def criado_em(self) -> datetime:
        return self._criado_em

    @property
    def empresa(self) -> str | None:
        return self._empresa

    @property
    def tipo_embalagem_interesse(self) -> str | None:
        return self._tipo_embalagem_interesse

    def abrir_orcamento(self, hoje: date) -> Orcamento:
        """Abre um novo Orçamento em NOVO_CONTATO para este cliente (RF01, RF08)."""
        return Orcamento.abrir(cliente_id=self._id, hoje=hoje)

    def atualizar_contato(self, *, telefone: Telefone, email: Email) -> None:
        self._telefone = telefone
        self._email = email
