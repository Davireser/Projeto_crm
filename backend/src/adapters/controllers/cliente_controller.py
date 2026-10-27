from uuid import UUID

from fastapi import APIRouter, status

from adapters.controllers.dependencias import Clientes, Orcamentos, RelogioDaApp
from adapters.schemas.cliente_schema import (
    ClienteDetalheSaida,
    ContatoRegistradoSaida,
    NovoContatoEntrada,
)
from adapters.schemas.interacao_schema import ItemHistoricoSaida
from application.use_cases.consultar_cliente import ConsultarClienteUseCase
from application.use_cases.consultar_historico_cliente import ConsultarHistoricoClienteUseCase
from application.use_cases.registrar_novo_contato import RegistrarNovoContatoUseCase

router = APIRouter(prefix="/clientes", tags=["clientes"])


@router.post("", status_code=status.HTTP_201_CREATED)
def registrar_novo_contato(
    entrada: NovoContatoEntrada, clientes: Clientes, orcamentos: Orcamentos, relogio: RelogioDaApp
) -> ContatoRegistradoSaida:
    """UC01: cria o Cliente e abre o primeiro Orçamento em NOVO_CONTATO."""
    use_case = RegistrarNovoContatoUseCase(clientes, orcamentos, relogio)
    return ContatoRegistradoSaida.de(use_case.executar(entrada.para_dados()))


@router.get("/{cliente_id}")
def consultar_cliente(
    cliente_id: UUID, clientes: Clientes, orcamentos: Orcamentos
) -> ClienteDetalheSaida:
    """UC09: o cliente com todos os seus orçamentos (RF08)."""
    resultado = ConsultarClienteUseCase(clientes, orcamentos).executar(cliente_id)
    return ClienteDetalheSaida.do_resultado(resultado)


@router.get("/{cliente_id}/historico")
def consultar_historico(
    cliente_id: UUID, clientes: Clientes, orcamentos: Orcamentos
) -> list[ItemHistoricoSaida]:
    """UC09: interações de todos os orçamentos do cliente, em ordem cronológica (RF07)."""
    itens = ConsultarHistoricoClienteUseCase(clientes, orcamentos).executar(cliente_id)
    return [ItemHistoricoSaida.do_item(item) for item in itens]
