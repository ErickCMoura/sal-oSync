"""Ponto de entrada: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.database import init_db
from app.errors import NaoEncontrado, RegraDeNegocio
from app.routes import console, pedidos, relatorios, testes, zonas


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


DESCRICAO = """
API do sistema de salão (pedidos de café/água, status das zonas e gamificação).

## Roteiro de teste (clique em *Try it out* em cada rota, nesta ordem)
1. `POST /testes/resetar` - começa do zero
2. `POST /pedidos` com `{"cadeira": 4, "tipo": "cafe"}` - botão de café da cadeira 4
3. `GET /pedidos/pendentes` - fila da copa: "Café para a Cadeira 04"
4. `POST /pedidos/concluir-proximo` com `{"funcionario": "ana"}` - entrega o pedido (+pontos)
5. `POST /zonas/2/suja` - câmera detectou sujeira na zona 2 (LED vermelho)
6. `GET /zonas/2` - estado: suja
7. `POST /zonas/2/limpeza/iniciar` com `{"funcionario": "ana"}` - em_limpeza (vermelho piscando)
8. `POST /zonas/2/limpeza/concluir` com `{"funcionario": "ana"}` - pronta (LED verde) + pontos
9. `GET /ranking` e `GET /metricas` - gamificação e tempos médios
10. `GET /console/2` - o que o ESP32 recebe para acender LEDs e buzzer

Erros esperados: tentar iniciar limpeza em zona que não está suja retorna **409**;
zona ou pedido inexistente retorna **404**.
"""

app = FastAPI(title="Salão IoT", description=DESCRICAO, version="1.0.0", lifespan=lifespan)

app.include_router(zonas.router)
app.include_router(pedidos.router)
app.include_router(relatorios.router)
app.include_router(console.router)
app.include_router(testes.router)


@app.exception_handler(NaoEncontrado)
async def _nao_encontrado(_: Request, exc: NaoEncontrado):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(RegraDeNegocio)
async def _regra(_: Request, exc: RegraDeNegocio):
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.get("/", tags=["Saúde"])
def raiz():
    return {"sistema": "Salão IoT", "status": "ok", "docs": "/docs"}
