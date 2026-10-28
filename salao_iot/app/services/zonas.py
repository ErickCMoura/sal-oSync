"""Regras das zonas: suja -> em_limpeza -> pronta."""
import random
import time

from app.config import NUM_CADEIRAS, PONTOS_LIMPEZA
from app.database import conexao
from app.errors import NaoEncontrado, RegraDeNegocio
from app.services import ranking


def _zona(conn, zona_id: int):
    row = conn.execute("SELECT * FROM zonas WHERE id = ?", (zona_id,)).fetchone()
    if row is None:
        raise NaoEncontrado(f"Zona {zona_id} não existe")
    return row


def _dict(row) -> dict:
    return {"id": row["id"], "estado": row["estado"], "responsavel": row["responsavel"]}


def listar() -> list[dict]:
    with conexao() as conn:
        return [_dict(r) for r in conn.execute("SELECT * FROM zonas ORDER BY id")]


def obter(zona_id: int) -> dict:
    with conexao() as conn:
        return _dict(_zona(conn, zona_id))


def marcar_suja(zona_id: int) -> dict:
    """Chamado pela câmera (visão computacional) ou pelo botão de atalho."""
    with conexao() as conn:
        zona = _zona(conn, zona_id)
        if zona["estado"] in ("suja", "em_limpeza"):
            return _dict(zona)  # já registrada, não reinicia o relógio
        conn.execute(
            """UPDATE zonas SET estado='suja', suja_em=?, limpeza_inicio=NULL,
               responsavel=NULL WHERE id=?""",
            (time.time(), zona_id),
        )
        return _dict(_zona(conn, zona_id))


def iniciar_limpeza(zona_id: int, funcionario: str) -> dict:
    with conexao() as conn:
        zona = _zona(conn, zona_id)
        if zona["estado"] != "suja":
            raise RegraDeNegocio(f"Zona {zona_id} não está suja (estado: {zona['estado']})")
        conn.execute(
            "UPDATE zonas SET estado='em_limpeza', limpeza_inicio=?, responsavel=? WHERE id=?",
            (time.time(), funcionario, zona_id),
        )
        return _dict(_zona(conn, zona_id))


def concluir_limpeza(zona_id: int, funcionario: str) -> dict:
    with conexao() as conn:
        zona = _zona(conn, zona_id)
        if zona["estado"] != "em_limpeza":
            raise RegraDeNegocio(f"Zona {zona_id} não está em limpeza (estado: {zona['estado']})")
        agora = time.time()
        tempo_resposta = zona["limpeza_inicio"] - zona["suja_em"]
        duracao = agora - zona["limpeza_inicio"]
        pontos = PONTOS_LIMPEZA + ranking.calcular_bonus(tempo_resposta)
        conn.execute(
            """INSERT INTO limpezas (zona_id, funcionario, suja_em, tempo_resposta_s,
               duracao_s, pontos, concluido_em) VALUES (?,?,?,?,?,?,?)""",
            (zona_id, funcionario, zona["suja_em"], tempo_resposta, duracao, pontos, agora),
        )
        conn.execute(
            """UPDATE zonas SET estado='pronta', suja_em=NULL, limpeza_inicio=NULL,
               responsavel=NULL WHERE id=?""",
            (zona_id,),
        )
        ranking.adicionar_pontos(conn, funcionario, pontos)
        return {
            **_dict(_zona(conn, zona_id)),
            "pontos_ganhos": pontos,
            "tempo_resposta_s": round(tempo_resposta, 1),
            "duracao_s": round(duracao, 1),
        }


def definir_estado(zona_id: int, estado: str) -> dict:
    """Ajuste manual (ex.: painel do gerente)."""
    with conexao() as conn:
        _zona(conn, zona_id)
        conn.execute(
            """UPDATE zonas SET estado=?, suja_em=?, limpeza_inicio=NULL, responsavel=NULL
               WHERE id=?""",
            (estado, time.time() if estado == "suja" else None, zona_id),
        )
        return _dict(_zona(conn, zona_id))


def simular_camera() -> dict:
    """Simula a visão computacional detectando sujeira numa zona livre."""
    livres = [z["id"] for z in listar() if z["estado"] in ("limpa", "pronta")]
    if not livres:
        raise RegraDeNegocio("Nenhuma zona livre para simular sujeira")
    return marcar_suja(random.choice(livres))
