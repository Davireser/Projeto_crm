"""Tipo de coluna DataHoraUTC: toda data e hora sai do banco em UTC, com fuso."""

from datetime import UTC, datetime, timedelta, timezone

import pytest
from sqlalchemy.dialects import sqlite

from infra.db.models import DataHoraUTC

pytestmark = pytest.mark.unit

DIALETO = sqlite.dialect()


def test_valor_nulo_continua_nulo() -> None:
    assert DataHoraUTC().process_bind_param(None, DIALETO) is None
    assert DataHoraUTC().process_result_value(None, DIALETO) is None


def test_data_sem_fuso_vinda_do_banco_e_tratada_como_utc() -> None:
    lida = DataHoraUTC().process_result_value(datetime(2026, 10, 13, 14, 43), DIALETO)

    assert lida == datetime(2026, 10, 13, 14, 43, tzinfo=UTC)


def test_data_com_outro_fuso_e_convertida_para_utc() -> None:
    brasilia = timezone(timedelta(hours=-3))
    local = datetime(2026, 10, 13, 11, 43, tzinfo=brasilia)

    gravada = DataHoraUTC().process_bind_param(local, DIALETO)

    assert gravada == datetime(2026, 10, 13, 14, 43, tzinfo=UTC)
    assert gravada is not None and gravada.tzinfo == UTC
