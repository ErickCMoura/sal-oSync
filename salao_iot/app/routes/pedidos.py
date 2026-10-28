from fastapi import APIRouter, status

from app.schemas import FuncionarioIn, PedidoIn
from app.services import pedidos

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


@router.post("", status_code=status.HTTP_201_CREATED)
def criar_pedido(dados: PedidoIn):
    """Botão físico da cadeira: café ou água."""
    return pedidos.criar(dados.cadeira, dados.tipo.value)


@router.get("/pendentes")
def listar_pendentes():
    """Terminal da copa: fila de pedidos em aberto."""
    return pedidos.pendentes()


@router.post("/concluir-proximo")
def concluir_proximo(dados: FuncionarioIn):
    return pedidos.concluir_proximo(dados.funcionario)


@router.post("/{pedido_id}/concluir")
def concluir_pedido(pedido_id: int, dados: FuncionarioIn):
    return pedidos.concluir(pedido_id, dados.funcionario)
