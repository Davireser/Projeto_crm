from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.orcamento import Orcamento


class OrcamentoRepository(ABC):
    """Porta de persistência do agregado Orcamento.

    Persiste o agregado inteiro, incluindo as Interações: não existe
    `InteracaoRepository` (decisão 2 de 08-decisao-arquitetura.md).
    """

    @abstractmethod
    def salvar(self, orcamento: Orcamento) -> None:
        """Insere ou atualiza o orçamento junto com suas interações."""

    @abstractmethod
    def buscar_por_id(self, orcamento_id: UUID) -> Orcamento | None: ...

    @abstractmethod
    def listar_todos(self) -> list[Orcamento]: ...

    @abstractmethod
    def listar_por_cliente(self, cliente_id: UUID) -> list[Orcamento]: ...
