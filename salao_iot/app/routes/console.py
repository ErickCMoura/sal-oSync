from fastapi import APIRouter

from app.services import pedidos, zonas

router = APIRouter(prefix="/console", tags=["Console (Arduino/ESP32)"])


@router.get("/{cadeira}")
def estado_do_console(cadeira: int):
    """Resposta enxuta para o microcontrolador acionar LEDs e buzzer."""
    return {
        "estado": zonas.obter(cadeira)["estado"],
        "pedidos_pendentes": pedidos.contar_pendentes(),
    }
