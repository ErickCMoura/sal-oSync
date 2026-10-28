from fastapi import APIRouter

from app import database

router = APIRouter(prefix="/testes", tags=["Testes"])


@router.post("/resetar")
def resetar():
    """Limpa pedidos, histórico e ranking e libera todas as zonas."""
    database.resetar()
    return {"detail": "Sistema resetado"}
