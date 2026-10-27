from uuid import UUID

from fastapi import APIRouter, status

from adapters.controllers.dependencias import HashDaApp, UsuarioLogado, Usuarios
from adapters.schemas.usuario_schema import EdicaoUsuarioEntrada, NovoUsuarioEntrada, UsuarioSaida
from application.use_cases.gerenciar_usuarios import GerenciarUsuariosUseCase

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get("")
def listar_usuarios(
    solicitante: UsuarioLogado, usuarios: Usuarios, hash_de_senha: HashDaApp
) -> list[UsuarioSaida]:
    """UC10: lista os usuários. Só Administrador (senão 403)."""
    lista = GerenciarUsuariosUseCase(usuarios, hash_de_senha).listar(solicitante)
    return [UsuarioSaida.de(u) for u in lista]


@router.post("", status_code=status.HTTP_201_CREATED)
def criar_usuario(
    entrada: NovoUsuarioEntrada,
    solicitante: UsuarioLogado,
    usuarios: Usuarios,
    hash_de_senha: HashDaApp,
) -> UsuarioSaida:
    """UC10: cria um usuário. E-mail repetido devolve 409."""
    criado = GerenciarUsuariosUseCase(usuarios, hash_de_senha).criar(
        solicitante, entrada.para_dados()
    )
    return UsuarioSaida.de(criado)


@router.patch("/{usuario_id}")
def editar_usuario(
    usuario_id: UUID,
    entrada: EdicaoUsuarioEntrada,
    solicitante: UsuarioLogado,
    usuarios: Usuarios,
    hash_de_senha: HashDaApp,
) -> UsuarioSaida:
    """UC10: edita nome, e-mail, perfil ou ativa/desativa. Auto-desativação devolve 422."""
    editado = GerenciarUsuariosUseCase(usuarios, hash_de_senha).editar(
        solicitante, usuario_id, entrada.para_dados()
    )
    return UsuarioSaida.de(editado)
