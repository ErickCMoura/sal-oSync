"""Acesso ao SQLite (histórico, pedidos, estado das zonas e pontuação)."""
import os
import sqlite3
from contextlib import contextmanager

from app.config import NUM_CADEIRAS

DB_PATH = os.getenv("SALAO_DB", "salao.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS zonas (
    id             INTEGER PRIMARY KEY,
    estado         TEXT NOT NULL DEFAULT 'pronta',
    suja_em        REAL,
    limpeza_inicio REAL,
    responsavel    TEXT
);
CREATE TABLE IF NOT EXISTS pedidos (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    cadeira      INTEGER NOT NULL,
    tipo         TEXT NOT NULL,
    status       TEXT NOT NULL DEFAULT 'pendente',
    criado_em    REAL NOT NULL,
    concluido_em REAL,
    atendido_por TEXT
);
CREATE TABLE IF NOT EXISTS limpezas (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    zona_id         INTEGER NOT NULL,
    funcionario     TEXT NOT NULL,
    suja_em         REAL NOT NULL,
    tempo_resposta_s REAL NOT NULL,
    duracao_s       REAL NOT NULL,
    pontos          INTEGER NOT NULL,
    concluido_em    REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS pontuacao (
    funcionario TEXT PRIMARY KEY,
    pontos      INTEGER NOT NULL DEFAULT 0
);
"""


@contextmanager
def conexao():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    with conexao() as conn:
        conn.executescript(SCHEMA)
        for zona_id in range(1, NUM_CADEIRAS + 1):
            conn.execute("INSERT OR IGNORE INTO zonas (id) VALUES (?)", (zona_id,))


def resetar():
    """Apaga o histórico e devolve todas as zonas ao estado 'pronta' (uso em testes)."""
    with conexao() as conn:
        for tabela in ("pedidos", "limpezas", "pontuacao"):
            conn.execute(f"DELETE FROM {tabela}")
        conn.execute(
            "UPDATE zonas SET estado='pronta', suja_em=NULL, limpeza_inicio=NULL, responsavel=NULL"
        )
