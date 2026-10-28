"""Gamificação: pontos e ranking da equipe."""
from app.config import BONUS_RAPIDEZ
from app.database import conexao


def calcular_bonus(segundos: float) -> int:
    for limite, pontos in BONUS_RAPIDEZ:
        if segundos <= limite:
            return pontos
    return 0


def adicionar_pontos(conn, funcionario: str, pontos: int) -> None:
    conn.execute(
        """INSERT INTO pontuacao (funcionario, pontos) VALUES (?, ?)
           ON CONFLICT(funcionario) DO UPDATE SET pontos = pontos + excluded.pontos""",
        (funcionario, pontos),
    )


def listar() -> list[dict]:
    with conexao() as conn:
        rows = conn.execute(
            "SELECT funcionario, pontos FROM pontuacao ORDER BY pontos DESC"
        ).fetchall()
    return [
        {"posicao": i + 1, "funcionario": r["funcionario"], "pontos": r["pontos"]}
        for i, r in enumerate(rows)
    ]
