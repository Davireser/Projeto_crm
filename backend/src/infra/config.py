"""Configuração vinda de variáveis de ambiente ou do arquivo .env (veja .env.example)."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_RAIZ_DO_PROJETO = Path(__file__).resolve().parents[3]

# Só serve para desenvolvimento; a aplicação se recusa a subir em produção com ele.
SEGREDO_JWT_PADRAO = "troque-este-valor-em-producao-por-um-segredo-longo"


class Configuracao(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(_RAIZ_DO_PROJETO / ".env", _RAIZ_DO_PROJETO / "backend" / ".env"),
        extra="ignore",
    )

    database_url: str = "postgresql+pg8000://crm:crm@localhost:5432/crm"
    # Banco só dos testes de integração: eles apagam e recriam as tabelas.
    test_database_url: str | None = None
    jwt_secret: str = SEGREDO_JWT_PADRAO
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 480
    api_v1_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:3000"
    environment: str = "development"
    # Fuso do negócio: define a data de abertura/fechamento dos orçamentos.
    fuso_horario: str = "America/Sao_Paulo"

    @property
    def origens_cors(self) -> list[str]:
        return [origem.strip() for origem in self.cors_origins.split(",") if origem.strip()]
