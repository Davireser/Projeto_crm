from typing import Self
from uuid import UUID

from adapters.schemas.base import Esquema, InstanteUTC, exemplo
from adapters.schemas.orcamento_schema import OrcamentoSaida
from application.use_cases.consultar_cliente import ClienteComOrcamentos
from application.use_cases.registrar_novo_contato import ContatoRegistrado, DadosNovoContato
from domain.entities.cliente import Cliente


class NovoContatoEntrada(Esquema):
    """Só os tipos são checados aqui; o formato de telefone e e-mail é regra do domínio (RF09)."""

    model_config = exemplo(
        {
            "nome": "Maria Souza",
            "telefone": "(31) 99876-5432",
            "email": "maria@embalagensabc.com.br",
            "empresa": "Embalagens ABC",
            "tipoEmbalagemInteresse": "Caixa de papelão",
        }
    )

    nome: str
    telefone: str
    email: str
    empresa: str | None = None
    tipo_embalagem_interesse: str | None = None

    def para_dados(self) -> DadosNovoContato:
        return DadosNovoContato(
            nome=self.nome,
            telefone=self.telefone,
            email=self.email,
            empresa=self.empresa,
            tipo_embalagem_interesse=self.tipo_embalagem_interesse,
        )


class ClienteSaida(Esquema):
    id: UUID
    nome: str
    telefone: str
    email: str
    empresa: str | None
    tipo_embalagem_interesse: str | None
    criado_em: InstanteUTC

    @classmethod
    def de(cls, cliente: Cliente) -> Self:
        return cls(
            id=cliente.id,
            nome=cliente.nome,
            telefone=cliente.telefone.numero,
            email=cliente.email.endereco,
            empresa=cliente.empresa,
            tipo_embalagem_interesse=cliente.tipo_embalagem_interesse,
            criado_em=cliente.criado_em,
        )


class ClienteDetalheSaida(ClienteSaida):
    orcamentos: list[OrcamentoSaida]

    @classmethod
    def do_resultado(cls, resultado: ClienteComOrcamentos) -> Self:
        base = ClienteSaida.de(resultado.cliente)
        return cls(
            **base.model_dump(),
            orcamentos=[OrcamentoSaida.de(o) for o in resultado.orcamentos],
        )


class ContatoRegistradoSaida(Esquema):
    cliente: ClienteSaida
    orcamento: OrcamentoSaida

    @classmethod
    def de(cls, contato: ContatoRegistrado) -> Self:
        return cls(
            cliente=ClienteSaida.de(contato.cliente),
            orcamento=OrcamentoSaida.de(contato.orcamento),
        )
