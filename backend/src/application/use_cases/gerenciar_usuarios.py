from dataclasses import dataclass
from uuid import UUID, uuid4

from application.exceptions import AcessoNegado, EmailJaCadastrado, UsuarioNaoEncontrado
from application.portas import HashDeSenha
from domain.entities.usuario import Administrador, Perfil, Usuario
from domain.exceptions import FormatoInvalido, OperacaoNaoPermitida
from domain.repositories.usuario_repository import UsuarioRepository
from domain.value_objects.email import Email

TAMANHO_MINIMO_DA_SENHA = 8


@dataclass(frozen=True)
class DadosNovoUsuario:
    nome: str
    email: str
    senha: str
    perfil: Perfil = Perfil.USUARIO


@dataclass(frozen=True)
class DadosEdicaoUsuario:
    """Campos omitidos (None) ficam como estão."""

    nome: str | None = None
    email: str | None = None
    ativo: bool | None = None
    perfil: Perfil | None = None


class GerenciarUsuariosUseCase:
    """UC10: só um Administrador ativo lista, cria e edita usuários (RF10, RNF07).

    A checagem de perfil fica aqui, não só na rota: mesmo chamado por outro
    caminho, um usuário comum não consegue gerenciar usuários.
    """

    def __init__(self, usuarios: UsuarioRepository, hash_de_senha: HashDeSenha) -> None:
        self._usuarios = usuarios
        self._hash = hash_de_senha

    def listar(self, solicitante: Usuario) -> list[Usuario]:
        _exigir_administrador(solicitante)
        return self._usuarios.listar_todos()

    def criar(self, solicitante: Usuario, dados: DadosNovoUsuario) -> Usuario:
        _exigir_administrador(solicitante)
        return self._criar(dados)

    def editar(self, solicitante: Usuario, usuario_id: UUID, dados: DadosEdicaoUsuario) -> Usuario:
        admin = _exigir_administrador(solicitante)
        usuario = self._usuarios.buscar_por_id(usuario_id)
        if usuario is None:
            raise UsuarioNaoEncontrado(usuario_id)

        if dados.nome is not None or dados.email is not None:
            email = Email(dados.email) if dados.email is not None else usuario.email
            self._garantir_email_livre(email, dono=usuario.id)
            usuario.atualizar_cadastro(nome=dados.nome or usuario.nome, email=email)
        if dados.ativo is True:
            admin.ativar_usuario(usuario)
        elif dados.ativo is False:
            admin.desativar_usuario(usuario)
        if dados.perfil is not None and dados.perfil is not usuario.perfil:
            usuario = admin.definir_perfil(usuario, dados.perfil)

        self._usuarios.salvar(usuario)
        return usuario

    def criar_primeiro_administrador(self, dados: DadosNovoUsuario) -> Administrador:
        """Cria o administrador inicial. Só funciona com o cadastro de usuários vazio."""
        if self._usuarios.listar_todos():
            raise OperacaoNaoPermitida(
                "Já existem usuários: novos usuários são criados por um administrador."
            )
        administrador = self._criar(
            DadosNovoUsuario(dados.nome, dados.email, dados.senha, Perfil.ADMINISTRADOR)
        )
        assert isinstance(administrador, Administrador)
        return administrador

    def _criar(self, dados: DadosNovoUsuario) -> Usuario:
        email = Email(dados.email)
        if len(dados.senha) < TAMANHO_MINIMO_DA_SENHA:
            raise FormatoInvalido(
                f"A senha precisa ter pelo menos {TAMANHO_MINIMO_DA_SENHA} caracteres.",
                campo="senha",
            )
        self._garantir_email_livre(email, dono=None)

        classe = Administrador if dados.perfil is Perfil.ADMINISTRADOR else Usuario
        usuario = classe(
            id=uuid4(), nome=dados.nome, email=email, senha_hash=self._hash.gerar(dados.senha)
        )
        self._usuarios.salvar(usuario)
        return usuario

    def _garantir_email_livre(self, email: Email, dono: UUID | None) -> None:
        existente = self._usuarios.buscar_por_email(email)
        if existente is not None and existente.id != dono:
            raise EmailJaCadastrado()


def _exigir_administrador(solicitante: Usuario) -> Administrador:
    if not isinstance(solicitante, Administrador) or not solicitante.ativo:
        raise AcessoNegado()
    return solicitante
