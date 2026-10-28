"""Pedidos de café e água feitos pelos botões de cada cadeira."""
import time

from app.config import NUM_CADEIRAS, PONTOS_PEDIDO
from app.database import conexao
from app.errors import NaoEncontrado, RegraDeNegocio
from app.services import ranking


def criar(cadeira: int, tipo: str) -> dict:
    if cadeira > NUM_CADEIRAS:
        raise NaoEncontrado(f"Cadeira {cadeira} não existe")
    with conexao() as conn:
        cur = conn.execute(
            "INSERT INTO pedidos (cadeira, tipo, criado_em) VALUES (?,?,?)",
            (cadeira, tipo, time.time()),
        )
        return {"id": cur.lastrowid, "cadeira": cadeira, "tipo": tipo, "status": "pendente"}


def pendentes() -> list[dict]:
    agora = time.time()
    with conexao() as conn:
        rows = conn.execute(
            "SELECT * FROM pedidos WHERE status='pendente' ORDER BY criado_em"
        ).fetchall()
    return [
        {
            "id": r["id"],
            "cadeira": r["cadeira"],
            "tipo": r["tipo"],
            "mensagem": f"{'Café' if r['tipo'] == 'cafe' else 'Água'} para a Cadeira {r['cadeira']:02d}",
            "espera_s": round(agora - r["criado_em"], 1),
        }
        for r in rows
    ]


def contar_pendentes() -> int:
    with conexao() as conn:
        return conn.execute("SELECT COUNT(*) FROM pedidos WHERE status='pendente'").fetchone()[0]


def _concluir(conn, pedido, funcionario: str) -> dict:
    agora = time.time()
    espera = agora - pedido["criado_em"]
    pontos = PONTOS_PEDIDO + ranking.calcular_bonus(espera)
    conn.execute(
        "UPDATE pedidos SET status='concluido', concluido_em=?, atendido_por=? WHERE id=?",
        (agora, funcionario, pedido["id"]),
    )
    ranking.adicionar_pontos(conn, funcionario, pontos)
    return {"id": pedido["id"], "status": "concluido", "pontos_ganhos": pontos,
            "tempo_atendimento_s": round(espera, 1)}


def concluir(pedido_id: int, funcionario: str) -> dict:
    with conexao() as conn:
        pedido = conn.execute("SELECT * FROM pedidos WHERE id=?", (pedido_id,)).fetchone()
        if pedido is None:
            raise NaoEncontrado(f"Pedido {pedido_id} não existe")
        if pedido["status"] != "pendente":
            raise RegraDeNegocio(f"Pedido {pedido_id} já foi concluído")
        return _concluir(conn, pedido, funcionario)


def concluir_proximo(funcionario: str) -> dict:
    """Conclui o pedido pendente mais antigo (útil para um botão físico único)."""
    with conexao() as conn:
        pedido = conn.execute(
            "SELECT * FROM pedidos WHERE status='pendente' ORDER BY criado_em LIMIT 1"
        ).fetchone()
        if pedido is None:
            raise RegraDeNegocio("Nenhum pedido pendente")
        return _concluir(conn, pedido, funcionario)
