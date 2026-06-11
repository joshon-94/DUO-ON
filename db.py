"""듀온 - SQLite 데이터베이스 헬퍼 (표준 라이브러리 sqlite3 사용)"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "duon.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            email         TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name          TEXT NOT NULL,
            gender        TEXT,            -- 'M' / 'F'
            birth_year    INTEGER,
            location      TEXT,
            bio           TEXT DEFAULT '',
            onboarded     INTEGER DEFAULT 0,
            created_at    TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS answers (
            user_id     INTEGER NOT NULL,
            question_id TEXT NOT NULL,
            value       TEXT NOT NULL,     -- single: 옵션키 / multi: 콤마구분 키들
            PRIMARY KEY (user_id, question_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS likes (
            from_user  INTEGER NOT NULL,
            to_user    INTEGER NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            PRIMARY KEY (from_user, to_user),
            FOREIGN KEY (from_user) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (to_user)   REFERENCES users(id) ON DELETE CASCADE
        );
        """
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("DB 초기화 완료:", DB_PATH)
