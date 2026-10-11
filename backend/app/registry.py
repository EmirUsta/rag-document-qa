import sqlite3
from contextlib import contextmanager

SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    doc_id TEXT PRIMARY KEY,
    original_filename TEXT NOT NULL,
    stored_filename TEXT NOT NULL,
    page_count INTEGER NOT NULL DEFAULT 0,
    chunk_count INTEGER NOT NULL DEFAULT 0,
    uploaded_at TEXT NOT NULL
);
"""


@contextmanager
def get_conn(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db(db_path: str) -> None:
    with get_conn(db_path) as conn:
        conn.execute(SCHEMA)


def insert_document(
    db_path: str,
    doc_id: str,
    original_filename: str,
    stored_filename: str,
    page_count: int,
    chunk_count: int,
    uploaded_at: str,
) -> None:
    with get_conn(db_path) as conn:
        conn.execute(
            "INSERT INTO documents "
            "(doc_id, original_filename, stored_filename, page_count, chunk_count, uploaded_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (doc_id, original_filename, stored_filename, page_count, chunk_count, uploaded_at),
        )


def list_documents(db_path: str) -> list[dict]:
    with get_conn(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM documents ORDER BY uploaded_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]


def get_document(db_path: str, doc_id: str) -> dict | None:
    with get_conn(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM documents WHERE doc_id = ?", (doc_id,)
        ).fetchone()
        return dict(row) if row else None


def delete_document(db_path: str, doc_id: str) -> dict | None:
    row = get_document(db_path, doc_id)
    if not row:
        return None
    with get_conn(db_path) as conn:
        conn.execute("DELETE FROM documents WHERE doc_id = ?", (doc_id,))
    return row
