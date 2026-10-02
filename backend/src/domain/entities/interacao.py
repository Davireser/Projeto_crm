from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from domain.value_objects.tipo_interacao import TipoInteracao


@dataclass(frozen=True)
class Interacao:
    """Registro imutável de um contato realizado.

    Pertence ao agregado `Orcamento` (composição) e só deve ser criada por
    `Orcamento.registrar_interacao()` — por isso não carrega `orcamento_id`.
    """

    id: UUID
    tipo: TipoInteracao
    conteudo: str
    data_hora: datetime
