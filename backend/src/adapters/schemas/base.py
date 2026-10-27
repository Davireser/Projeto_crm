from datetime import UTC, datetime
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from pydantic.config import JsonDict


class Esquema(BaseModel):
    """Base dos schemas da API: Python em snake_case, JSON em camelCase (especificações §7)."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, frozen=True)


InstanteUTC = Annotated[datetime, AfterValidator(lambda instante: instante.astimezone(UTC))]
"""Horário que sai na API sempre em UTC ("...Z"), venha do relógio local ou do banco."""


def exemplo(dados: JsonDict) -> ConfigDict:
    """Exemplo válido que aparece já preenchido no /docs ao clicar em "Try it out".

    Sem ele, o Swagger preenche tudo com a palavra "string", que a API recusa.
    As chaves usam camelCase, como o JSON de verdade.
    """
    return ConfigDict(json_schema_extra={"examples": [dados]})
