# Salão IoT (Python + FastAPI + ESP32 no Wokwi)

## Estrutura
```
salao_iot/
├── app/
│   ├── main.py          # cria a API e registra as rotas
│   ├── config.py        # nº de cadeiras e regras de pontuação
│   ├── database.py      # SQLite (zonas, pedidos, limpezas, pontuação)
│   ├── schemas.py       # validação dos dados de entrada
│   ├── errors.py        # erros de negócio (404 / 409)
│   ├── routes/          # rotas HTTP (finas, só chamam os services)
│   └── services/        # regras do sistema
└── firmware/            # sketch.ino, diagram.json, libraries.txt (Wokwi)
```

## 1. Rodar a API
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate   |   Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Teste as rotas no Swagger: http://localhost:8000/docs (o roteiro de teste aparece no topo da página)

## 2. Expor a API para o Wokwi
O Wokwi roda na nuvem e não enxerga seu `localhost`. Use um túnel:
```bash
ngrok http 8000
```
Copie a URL `https://xxxx.ngrok-free.app` e cole em `API_URL` no `sketch.ino`.

## 3. Montar o circuito no Wokwi
1. Em wokwi.com crie um projeto **ESP32**.
2. Substitua o conteúdo de `sketch.ino`, `diagram.json` e `libraries.txt` pelos arquivos de `firmware/`.
3. Inicie a simulação e acompanhe o Monitor Serial.

| Componente | Pino ESP32 |
|---|---|
| Botão Café / Água / Suja / Limpeza / Copa | 12 / 13 / 14 / 15 / 4 |
| LED verde / LED vermelho | 26 / 27 |
| Buzzer | 33 |

## Rotas
| Método | Rota | Função |
|---|---|---|
| POST | `/pedidos` | botão de café/água `{"cadeira":4,"tipo":"cafe"}` |
| GET | `/pedidos/pendentes` | fila da copa ("Café para a Cadeira 04") |
| POST | `/pedidos/{id}/concluir` | conclui um pedido `{"funcionario":"ana"}` |
| POST | `/pedidos/concluir-proximo` | conclui o pedido mais antigo |
| GET | `/zonas` | status de todas as zonas (painel central) |
| GET | `/zonas/{id}` | status de uma zona |
| POST | `/zonas/{id}/suja` | câmera/botão avisa sujeira |
| POST | `/zonas/{id}/limpeza/iniciar` | inicia limpeza (zona vermelha) |
| POST | `/zonas/{id}/limpeza/concluir` | conclui, libera a zona e dá pontos |
| PUT | `/zonas/{id}/estado` | ajuste manual de estado |
| POST | `/zonas/simular-camera` | simula a visão computacional |
| GET | `/console/{cadeira}` | resposta enxuta para LEDs/buzzer do ESP32 |
| GET | `/ranking` | ranking da gamificação |
| GET | `/metricas` | tempos médios e horários de pico de sujeira |
| POST | `/testes/resetar` | zera pedidos, ranking e zonas (só para testes) |

## Pontuação (editável em `app/config.py`)
Pedido entregue = 5 pts. Limpeza concluída = 10 pts. Bônus: início em até 60 s = +5, até 180 s = +2.

## Fluxo de teste rápido
1. Aperte **Suja** → LED vermelho fixo.
2. Aperte **Limpeza** → vermelho piscando (em limpeza).
3. Aperte **Limpeza** de novo → LED verde e pontos para `copa-01`.
4. Aperte **Café** → buzzer toca; **Copa** conclui o pedido.
5. Veja `/ranking` e `/metricas`.
