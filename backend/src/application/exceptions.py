"""Exceções da camada de aplicação.

Diferente das exceções de domínio (regra violada → 422), estas indicam que o
recurso pedido não existe — na API viram 404.
"""

from uuid import UUID


class RecursoNaoEncontrado(Exception):
    def __init__(self, recurso: str, recurso_id: UUID) -> None:
        self.recurso = recurso
        self.recurso_id = recurso_id
        self.mensagem = f"{recurso} {recurso_id} não encontrado."
        super().__init__(self.mensagem)


class ClienteNaoEncontrado(RecursoNaoEncontrado):
    def __init__(self, cliente_id: UUID) -> None:
        super().__init__("Cliente", cliente_id)


class OrcamentoNaoEncontrado(RecursoNaoEncontrado):
    def __init__(self, orcamento_id: UUID) -> None:
        super().__init__("Orçamento", orcamento_id)


class UsuarioNaoEncontrado(RecursoNaoEncontrado):
    def __init__(self, usuario_id: UUID) -> None:
        super().__init__("Usuário", usuario_id)


class ErroDeAcesso(Exception):
    """Base dos erros de autenticação e autorização."""

    def __init__(self, mensagem: str, campo: str | None = None) -> None:
        self.mensagem = mensagem
        self.campo = campo
        super().__init__(mensagem)


class CredenciaisInvalidas(ErroDeAcesso):
    """Login recusado (401). A mensagem é a mesma para e-mail e senha errados."""

    def __init__(self) -> None:
        super().__init__("E-mail ou senha incorretos.")


class NaoAutenticado(ErroDeAcesso):
    """Requisição sem token válido (401)."""

    def __init__(self) -> None:
        super().__init__("É preciso entrar no sistema para acessar este recurso.")


class AcessoNegado(ErroDeAcesso):
    """Usuário autenticado, mas sem o perfil necessário (403)."""

    def __init__(self) -> None:
        super().__init__("Apenas administradores podem realizar esta operação.")


class EmailJaCadastrado(ErroDeAcesso):
    """Já existe usuário com este e-mail (409)."""

    def __init__(self) -> None:
        super().__init__("Já existe um usuário com este e-mail.", campo="email")
