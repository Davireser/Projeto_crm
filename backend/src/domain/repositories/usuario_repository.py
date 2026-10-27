from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.usuario import Usuario
from domain.value_objects.email import Email


class UsuarioRepository(ABC):
    """Porta de persistência de Usuario e Administrador (mesma tabela, coluna `perfil`)."""

    @abstractmethod
    def salvar(self, usuario: Usuario) -> None: ...

    @abstractmethod
    def buscar_por_id(self, usuario_id: UUID) -> Usuario | None: ...

    @abstractmethod
    def buscar_por_email(self, email: Email) -> Usuario | None: ...

    @abstractmethod
    def listar_todos(self) -> list[Usuario]: ...
