from dataclasses import dataclass

from application.relogio import Relogio
from domain.entities.cliente import Cliente
from domain.entities.orcamento import Orcamento
from domain.repositories.cliente_repository import ClienteRepository
from domain.repositories.orcamento_repository import OrcamentoRepository
from domain.value_objects.email import Email
from domain.value_objects.telefone import Telefone


@dataclass(frozen=True)
class DadosNovoContato:
    nome: str
    telefone: str
    email: str
    empresa: str | None = None
    tipo_embalagem_interesse: str | None = None


@dataclass(frozen=True)
class ContatoRegistrado:
    cliente: Cliente
    orcamento: Orcamento


class RegistrarNovoContatoUseCase:
    """UC01 (inclui UC02): cria o Cliente e abre o primeiro Orçamento em NOVO_CONTATO.

    Toda a validação acontece na construção dos Value Objects e da entidade,
    antes do primeiro `salvar()` — dado inválido não deixa nada persistido (RF01).
    A atomicidade das duas escritas fica com a transação por requisição (Parte 3).
    """

    def __init__(
        self, clientes: ClienteRepository, orcamentos: OrcamentoRepository, relogio: Relogio
    ) -> None:
        self._clientes = clientes
        self._orcamentos = orcamentos
        self._relogio = relogio

    def executar(self, dados: DadosNovoContato) -> ContatoRegistrado:
        agora = self._relogio()
        cliente = Cliente.cadastrar(
            nome=dados.nome,
            telefone=Telefone(dados.telefone),
            email=Email(dados.email),
            empresa=dados.empresa,
            tipo_embalagem_interesse=dados.tipo_embalagem_interesse,
            agora=agora,
        )
        orcamento = cliente.abrir_orcamento(hoje=agora.date())

        self._clientes.salvar(cliente)
        self._orcamentos.salvar(orcamento)
        return ContatoRegistrado(cliente=cliente, orcamento=orcamento)
