from application.exceptions import CredenciaisInvalidas
from application.portas import HashDeSenha
from domain.entities.usuario import Usuario
from domain.exceptions import FormatoInvalido
from domain.repositories.usuario_repository import UsuarioRepository
from domain.value_objects.email import Email

# Conferido quando o e-mail não existe, para o login demorar o mesmo tempo
# nos dois casos e não revelar quais e-mails estão cadastrados.
_HASH_DE_REFERENCIA = (
    "scrypt$16384$8$1$AAAAAAAAAAAAAAAAAAAAAA==$AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
)


class AutenticarUsuarioUseCase:
    """Confere e-mail e senha (RNF07). O token é emitido pela API, não aqui."""

    def __init__(self, usuarios: UsuarioRepository, hash_de_senha: HashDeSenha) -> None:
        self._usuarios = usuarios
        self._hash = hash_de_senha

    def executar(self, email: str, senha: str) -> Usuario:
        try:
            usuario = self._usuarios.buscar_por_email(Email(email))
        except FormatoInvalido:
            usuario = None

        if usuario is None:
            self._hash.confere(senha, _HASH_DE_REFERENCIA)
            raise CredenciaisInvalidas()
        if not self._hash.confere(senha, usuario.senha_hash) or not usuario.ativo:
            raise CredenciaisInvalidas()
        return usuario
