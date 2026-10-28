"""Modelos de entrada das rotas (validação automática)."""
from enum import Enum

from pydantic import BaseModel, Field


class TipoPedido(str, Enum):
    cafe = "cafe"
    agua = "agua"


class EstadoZona(str, Enum):
    limpa = "limpa"
    suja = "suja"
    em_limpeza = "em_limpeza"
    pronta = "pronta"


class PedidoIn(BaseModel):
    cadeira: int = Field(ge=1, examples=[4])
    tipo: TipoPedido


class FuncionarioIn(BaseModel):
    funcionario: str = Field(min_length=1, max_length=40, examples=["copa-01"])


class EstadoIn(BaseModel):
    estado: EstadoZona
