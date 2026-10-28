"""Métricas de operação (tempo médio e horários de pico de sujeira)."""
from app.database import conexao


def _arred(valor):
    return None if valor is None else round(valor, 1)


def resumo() -> dict:
    with conexao() as conn:
        tempo_pedido = conn.execute(
            "SELECT AVG(concluido_em - criado_em) FROM pedidos WHERE status='concluido'"
        ).fetchone()[0]
        tempo_resposta = conn.execute("SELECT AVG(tempo_resposta_s) FROM limpezas").fetchone()[0]
        total_limpezas = conn.execute("SELECT COUNT(*) FROM limpezas").fetchone()[0]
        pendentes = conn.execute(
            "SELECT COUNT(*) FROM pedidos WHERE status='pendente'"
        ).fetchone()[0]
        picos = conn.execute(
            """SELECT strftime('%H', suja_em, 'unixepoch', 'localtime') AS hora, COUNT(*) AS total
               FROM limpezas GROUP BY hora ORDER BY total DESC"""
        ).fetchall()
    return {
        "tempo_medio_pedido_s": _arred(tempo_pedido),
        "tempo_medio_resposta_limpeza_s": _arred(tempo_resposta),
        "total_limpezas": total_limpezas,
        "pedidos_pendentes": pendentes,
        "picos_sujeira_por_hora": [{"hora": f"{r['hora']}h", "ocorrencias": r["total"]} for r in picos],
    }
