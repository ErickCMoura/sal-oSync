from fastapi import APIRouter

from app.services import metricas, ranking

router = APIRouter(tags=["Relatórios"])


@router.get("/ranking")
def obter_ranking():
    return ranking.listar()


@router.get("/metricas")
def obter_metricas():
    return metricas.resumo()
