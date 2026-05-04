import sqlite3
import logging
import os

logger = logging.getLogger(__name__)


def init_db(db_path: str):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile TEXT NOT NULL,
            account_name TEXT,
            mail_id TEXT NOT NULL,
            sender TEXT,
            recipients TEXT,
            cc TEXT,
            subject TEXT,
            date_text TEXT,
            text_body TEXT,
            html_body TEXT,
            attachments_json TEXT,
            header_raw TEXT,
            raw_json TEXT,
            is_read INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(profile, mail_id)
        );
    """)
    conn.commit()
    conn.close()
    logger.info("数据库初始化完成: %s", db_path)


def insert_email(db_path: str, email_data: dict):
    keys = list(email_data.keys())
    placeholders = ", ".join(["?"] * len(keys))
    columns = ", ".join(keys)
    sql = f"INSERT OR IGNORE INTO emails ({columns}) VALUES ({placeholders})"
    values = [email_data[k] for k in keys]
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.execute(sql, values)
        conn.commit()
        if cursor.rowcount > 0:
            logger.info("Email inserted: profile=%s, mail_id=%s", email_data.get("profile"), email_data.get("mail_id"))
        else:
            logger.info("Email ignored (duplicate): profile=%s, mail_id=%s", email_data.get("profile"), email_data.get("mail_id"))
        conn.close()
    except Exception as e:
        logger.error("Failed to insert email: %s", e)


def get_emails(db_path: str, limit: int = 300) -> list[dict]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM emails ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_email_by_id(db_path: str, email_id: int) -> dict | None:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT * FROM emails WHERE id = ?", (email_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def mark_as_read(db_path: str, email_id: int):
    conn = sqlite3.connect(db_path)
    conn.execute("UPDATE emails SET is_read = 1 WHERE id = ?", (email_id,))
    conn.commit()
    conn.close()
