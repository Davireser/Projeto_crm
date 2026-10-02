"""Exceções de domínio.

Cada exceção carrega `mensagem` e `campo`, que a camada de adapters converte
diretamente no formato de erro da API: `{"erro", "mensagem", "campo"}`.
"""


class ErroDominio(Exception):
    def __init__(self, mensagem: str, campo: str | None = None) -> None:
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.campo = campo


class TransicaoInvalida(ErroDominio):
    """Par origem→destino fora do funil ou guarda de valor violada (RF02, RF03)."""


class FormatoInvalido(ErroDominio):
    """Dado de entrada em formato inválido — telefone, e-mail, nome, conteúdo (RF09)."""


class ValorInvalido(ErroDominio):
    """Valor orçado zero, negativo ou com mais de duas casas decimais (RN06)."""


class OperacaoNaoPermitida(ErroDominio):
    """Operação proibida pela regra de negócio, como a auto-desativação (RF10)."""
