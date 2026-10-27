"""Hash de senha (scrypt) e token JWT (RNF07)."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
import pytest

from domain.entities.usuario import Administrador
from domain.value_objects.email import Email
from infra.security import EmissorJWT, HashScrypt, TokenInvalido
from relogio_de_teste import RelogioDeTeste

pytestmark = pytest.mark.unit

SEGREDO = "segredo-de-teste-com-mais-de-32-bytes!!"
AGORA = datetime(2026, 9, 15, 14, 30, tzinfo=UTC)

# Custo baixo só para os testes ficarem rápidos; a aplicação usa o padrão.
hash_rapido = HashScrypt(n=2**10)


# --- Hash de senha -----------------------------------------------------------


def test_senha_certa_confere_e_errada_nao() -> None:
    guardado = hash_rapido.gerar("minha-senha")

    assert hash_rapido.confere("minha-senha", guardado)
    assert not hash_rapido.confere("outra-senha", guardado)


def test_hash_nao_contem_a_senha_e_muda_a_cada_vez() -> None:
    primeiro, segundo = hash_rapido.gerar("minha-senha"), hash_rapido.gerar("minha-senha")

    assert "minha-senha" not in primeiro
    assert primeiro != segundo  # sal aleatório
    assert primeiro.startswith("scrypt$")


@pytest.mark.parametrize("lixo", ["", "texto-qualquer", "scrypt$1$2", "bcrypt$a$b$c$d$e"])
def test_hash_mal_formado_nunca_confere(lixo: str) -> None:
    assert not hash_rapido.confere("qualquer", lixo)


def test_confere_hash_gerado_com_outro_custo() -> None:
    guardado = HashScrypt(n=2**11).gerar("minha-senha")

    assert hash_rapido.confere("minha-senha", guardado)


# --- Token JWT ---------------------------------------------------------------


@pytest.fixture
def relogio() -> RelogioDeTeste:
    return RelogioDeTeste(AGORA)


@pytest.fixture
def emissor(relogio: RelogioDeTeste) -> EmissorJWT:
    return EmissorJWT(SEGREDO, "HS256", validade_minutos=60, relogio=relogio)


def admin() -> Administrador:
    return Administrador(id=uuid4(), nome="Admin", email=Email("a@crm.com"), senha_hash="h")


def test_token_emitido_e_lido_de_volta(emissor: EmissorJWT) -> None:
    usuario = admin()

    token = emissor.emitir(usuario)

    assert emissor.ler(token.valor) == usuario.id
    assert token.expira_em == AGORA + timedelta(minutes=60)


def test_token_leva_o_perfil_mas_nunca_a_senha(emissor: EmissorJWT) -> None:
    conteudo = jwt.decode(
        emissor.emitir(admin()).valor, SEGREDO, algorithms=["HS256"], options={"verify_exp": False}
    )

    assert conteudo["perfil"] == "ADMINISTRADOR"
    assert "senha_hash" not in conteudo


def test_token_expira(emissor: EmissorJWT, relogio: RelogioDeTeste) -> None:
    token = emissor.emitir(admin()).valor

    relogio.avancar(minutos=61)

    with pytest.raises(TokenInvalido):
        emissor.ler(token)


def test_token_assinado_com_outro_segredo_e_recusado(relogio: RelogioDeTeste) -> None:
    falsificador = EmissorJWT("outro-segredo-tambem-bem-comprido!!", "HS256", 60, relogio)
    token = falsificador.emitir(admin()).valor

    with pytest.raises(TokenInvalido):
        EmissorJWT(SEGREDO, "HS256", 60, relogio).ler(token)


@pytest.mark.parametrize("lixo", ["", "abc", "a.b.c"])
def test_token_lixo_e_recusado(emissor: EmissorJWT, lixo: str) -> None:
    with pytest.raises(TokenInvalido):
        emissor.ler(lixo)


def test_expiracao_informada_bate_com_a_do_token(relogio: RelogioDeTeste) -> None:
    relogio.agora = AGORA.replace(microsecond=654321)
    emissor = EmissorJWT(SEGREDO, "HS256", validade_minutos=60, relogio=relogio)

    token = emissor.emitir(admin())

    conteudo = jwt.decode(token.valor, SEGREDO, algorithms=["HS256"], options={"verify_exp": False})
    assert token.expira_em.timestamp() == conteudo["exp"]
