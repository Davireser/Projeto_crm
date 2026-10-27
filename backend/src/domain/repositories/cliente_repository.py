from abc import ABC, abstractmethod
from collections.abc import Iterable
from uuid import UUID

from domain.entities.cliente import Cliente


class ClienteRepository(ABC):
    """Porta de persistência do agregado Cliente. Implementações ficam em adapters/."""

    @abstractmethod
    def salvar(self, cliente: Cliente) -> None:
        """Insere ou atualiza o cliente."""

    @abstractmethod
    def buscar_por_id(self, cliente_id: UUID) -> Cliente | None: ...

    @abstractmethod
    def listar_por_ids(self, cliente_ids: Iterable[UUID]) -> list[Cliente]:
        """Clientes cujos ids estão em `cliente_ids`; ids desconhecidos são ignorados."""
