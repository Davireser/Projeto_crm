"""Teste de arquitetura (RNF03).

Garante a regra de dependência da Clean Architecture: `domain/` e `application/`
não importam framework nem camadas mais externas. A verificação é feita por
análise estática (ast), então roda sem instalar nenhum framework.
"""

import ast
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[2] / "src"

FRAMEWORKS_PROIBIDOS = frozenset(
    {"fastapi", "starlette", "sqlalchemy", "pydantic", "alembic", "jose", "jwt", "passlib"}
)

CAMADAS_PROIBIDAS: dict[str, frozenset[str]] = {
    "domain": frozenset({"application", "adapters", "infra", "main"}),
    "application": frozenset({"adapters", "infra", "main"}),
}


def modulos_importados(codigo: str) -> set[str]:
    """Devolve o pacote de primeiro nível de cada import absoluto do código."""
    modulos: set[str] = set()
    for no in ast.walk(ast.parse(codigo)):
        if isinstance(no, ast.Import):
            modulos.update(alias.name.split(".")[0] for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.level == 0 and no.module:
            modulos.add(no.module.split(".")[0])
    return modulos


def violacoes(camada: str, codigo: str) -> set[str]:
    proibidos = FRAMEWORKS_PROIBIDOS | CAMADAS_PROIBIDAS[camada]
    return modulos_importados(codigo) & proibidos


def arquivos_da_camada(camada: str) -> list[Path]:
    return sorted((SRC / camada).rglob("*.py"))


@pytest.mark.unit
@pytest.mark.parametrize("camada", sorted(CAMADAS_PROIBIDAS))
def test_camada_interna_nao_importa_framework_nem_camada_externa(camada: str) -> None:
    arquivos = arquivos_da_camada(camada)
    assert arquivos, f"camada {camada}/ não encontrada em {SRC}"

    encontradas = {
        str(arquivo.relative_to(SRC)): sorted(proibidos)
        for arquivo in arquivos
        if (proibidos := violacoes(camada, arquivo.read_text(encoding="utf-8")))
    }

    assert not encontradas, f"Imports proibidos em {camada}/: {encontradas}"


@pytest.mark.unit
@pytest.mark.parametrize(
    ("camada", "codigo", "esperado"),
    [
        ("domain", "import fastapi", {"fastapi"}),
        ("domain", "from sqlalchemy.orm import Session", {"sqlalchemy"}),
        ("domain", "from pydantic import BaseModel", {"pydantic"}),
        ("domain", "from infra.db.models import OrcamentoModel", {"infra"}),
        ("domain", "from application.use_cases import x", {"application"}),
        ("application", "from adapters.schemas import x", {"adapters"}),
        ("application", "from domain.entities.orcamento import Orcamento", set()),
        ("domain", "from dataclasses import dataclass", set()),
        ("domain", "from .exceptions import TransicaoInvalida", set()),
    ],
)
def test_verificador_detecta_imports_proibidos(
    camada: str, codigo: str, esperado: set[str]
) -> None:
    assert violacoes(camada, codigo) == esperado
