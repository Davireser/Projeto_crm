from collections.abc import Callable
from datetime import datetime

type Relogio = Callable[[], datetime]
"""Fonte do "agora" injetada nos casos de uso.

Em produção é algo como `lambda: datetime.now(UTC)`; nos testes, um valor fixo.
Assim o domínio nunca chama `datetime.now()` e os testes são determinísticos.
"""
