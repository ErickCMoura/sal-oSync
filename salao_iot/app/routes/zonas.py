from fastapi import APIRouter

from app.schemas import EstadoIn, FuncionarioIn
from app.services import zonas

router = APIRouter(prefix="/zonas", tags=["Zonas"])


@router.get("")
def listar_zonas():
    """Status de todas as zonas (painel central)."""
    return zonas.listar()


@router.post("/simular-camera")
def simular_camera():
    """Simula a câmera detectando sujeira em uma zona livre aleatória."""
    return zonas.simular_camera()


@router.get("/{zona_id}")
def obter_zona(zona_id: int):
    return zonas.obter(zona_id)


@router.post("/{zona_id}/suja")
def marcar_suja(zona_id: int):
    """Câmera (ou botão de atalho) avisa que a zona está suja."""
    return zonas.marcar_suja(zona_id)


@router.post("/{zona_id}/limpeza/iniciar")
def iniciar_limpeza(zona_id: int, dados: FuncionarioIn):
    return zonas.iniciar_limpeza(zona_id, dados.funcionario)


@router.post("/{zona_id}/limpeza/concluir")
def concluir_limpeza(zona_id: int, dados: FuncionarioIn):
    return zonas.concluir_limpeza(zona_id, dados.funcionario)


@router.put("/{zona_id}/estado")
def definir_estado(zona_id: int, dados: EstadoIn):
    return zonas.definir_estado(zona_id, dados.estado.value)
