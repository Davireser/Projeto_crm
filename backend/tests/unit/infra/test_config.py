"""Configuração lida de variáveis de ambiente (especificacoes_tecnicas.md §6)."""

import pytest

from infra.config import Configuracao

pytestmark = pytest.mark.unit


def test_le_variaveis_de_ambiente(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+pg8000://u:s@db:5432/crm")
    monkeypatch.setenv("JWT_EXPIRATION_MINUTES", "60")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")

    config = Configuracao(_env_file=None)

    assert config.database_url == "postgresql+pg8000://u:s@db:5432/crm"
    assert config.jwt_expiration_minutes == 60
    assert config.origens_cors == ["http://localhost:3000", "http://127.0.0.1:3000"]


def test_tem_valores_padrao_para_desenvolvimento(monkeypatch: pytest.MonkeyPatch) -> None:
    for variavel in (
        "DATABASE_URL",
        "JWT_EXPIRATION_MINUTES",
        "CORS_ORIGINS",
        "ENVIRONMENT",
        "FUSO_HORARIO",
    ):
        monkeypatch.delenv(variavel, raising=False)

    config = Configuracao(_env_file=None)

    assert config.database_url.startswith("postgresql+pg8000://")
    assert config.api_v1_prefix == "/api/v1"
    assert config.environment == "development"
    assert config.fuso_horario == "America/Sao_Paulo"
