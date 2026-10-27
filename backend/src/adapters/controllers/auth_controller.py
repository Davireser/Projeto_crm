from fastapi import APIRouter

from adapters.controllers.dependencias import EmissorDaApp, HashDaApp, UsuarioLogado, Usuarios
from adapters.schemas.usuario_schema import LoginEntrada, TokenSaida, UsuarioSaida
from application.use_cases.autenticar_usuario import AutenticarUsuarioUseCase

router = APIRouter(prefix="/auth", tags=["autenticacao"])


@router.post("/login")
def login(
    entrada: LoginEntrada, usuarios: Usuarios, hash_de_senha: HashDaApp, emissor: EmissorDaApp
) -> TokenSaida:
    """Troca e-mail e senha por um token. Única rota que não exige token."""
    usuario = AutenticarUsuarioUseCase(usuarios, hash_de_senha).executar(
        entrada.email, entrada.senha
    )
    token = emissor.emitir(usuario)
    return TokenSaida(
        access_token=token.valor, expira_em=token.expira_em, usuario=UsuarioSaida.de(usuario)
    )


@router.get("/eu")
def quem_sou_eu(usuario: UsuarioLogado) -> UsuarioSaida:
    """Dados de quem está logado — o frontend usa para saber o nome e o perfil."""
    return UsuarioSaida.de(usuario)
