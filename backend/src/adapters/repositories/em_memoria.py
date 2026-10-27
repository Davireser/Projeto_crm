"""Repositórios em memória (RNF06).

Usados nos testes de casos de uso e úteis para rodar a aplicação sem banco.
Guardam e devolvem **cópias** dos agregados, imitando um banco de verdade:
alterar um objeto carregado não muda nada até que `salvar()` seja chamado.
"""

from collections.abc import Iterable
from copy import deepcopy
from typing import Protocol
from uuid import UUID

from domain.entities.cliente import Cliente
from domain.entities.orcamento import Orcamento
from domain.entities.usuario import Usuario
from domain.repositories.cliente_repository import ClienteRepository
from domain.repositories.orcamento_repository import OrcamentoRepository
from domain.repositories.usuario_repository import UsuarioRepository
from domain.value_objects.email import Email


class _ComId(Protocol):
    @property
    def id(self) -> UUID: ...


class _Armazem[T: _ComId]:
    def __init__(self) -> None:
        self._dados: dict[UUID, T] = {}
        self.salvamentos = 0
        """Quantas vezes `salvar()` foi chamado — usado nos testes de RNF04."""

    def salvar(self, item: T) -> None:
        self._dados[item.id] = deepcopy(item)
        self.salvamentos += 1

    def _buscar(self, item_id: UUID) -> T | None:
        item = self._dados.get(item_id)
        return deepcopy(item) if item is not None else None

    def _todos(self) -> list[T]:
        return [deepcopy(item) for item in self._dados.values()]


class ClienteRepositoryEmMemoria(_Armazem[Cliente], ClienteRepository):
    def buscar_por_id(self, cliente_id: UUID) -> Cliente | None:
        return self._buscar(cliente_id)

    def listar_por_ids(self, cliente_ids: Iterable[UUID]) -> list[Cliente]:
        procurados = set(cliente_ids)
        return [c for c in self._todos() if c.id in procurados]


class OrcamentoRepositoryEmMemoria(_Armazem[Orcamento], OrcamentoRepository):
    def buscar_por_id(self, orcamento_id: UUID) -> Orcamento | None:
        return self._buscar(orcamento_id)

    def listar_todos(self) -> list[Orcamento]:
        return self._todos()

    def listar_por_cliente(self, cliente_id: UUID) -> list[Orcamento]:
        return [o for o in self._todos() if o.cliente_id == cliente_id]


class UsuarioRepositoryEmMemoria(_Armazem[Usuario], UsuarioRepository):
    def buscar_por_id(self, usuario_id: UUID) -> Usuario | None:
        return self._buscar(usuario_id)

    def buscar_por_email(self, email: Email) -> Usuario | None:
        return next((u for u in self._todos() if u.email == email), None)

    def listar_todos(self) -> list[Usuario]:
        return self._todos()
