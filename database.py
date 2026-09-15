import sqlite3
from pathlib import Path
from datetime import datetime, timezone


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "publisher.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def now():
    return datetime.now(timezone.utc).isoformat()


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            language TEXT NOT NULL DEFAULT 'ar',
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            channel_id TEXT NOT NULL,
            username TEXT,
            title TEXT,
            created_at TEXT NOT NULL,
            UNIQUE(user_id, channel_id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            channel_id TEXT NOT NULL,
            text TEXT,
            media_type TEXT,
            media_path TEXT,
            buttons TEXT,
            status TEXT NOT NULL DEFAULT 'published',
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


def get_user(telegram_id):
    conn = get_connection()

    row = conn.execute(
        "SELECT * FROM users WHERE telegram_id = ?",
        (telegram_id,)
    ).fetchone()

    conn.close()
    return row


def create_user(telegram_id, language="ar"):
    conn = get_connection()

    conn.execute(
        """
        INSERT OR IGNORE INTO users
        (telegram_id, language, created_at)
        VALUES (?, ?, ?)
        """,
        (telegram_id, language, now())
    )

    conn.commit()

    row = conn.execute(
        "SELECT * FROM users WHERE telegram_id = ?",
        (telegram_id,)
    ).fetchone()

    conn.close()
    return row


def set_language(telegram_id, language):
    conn = get_connection()

    conn.execute(
        """
        UPDATE users
        SET language = ?
        WHERE telegram_id = ?
        """,
        (language, telegram_id)
    )

    conn.commit()
    conn.close()


def get_language(telegram_id):
    user = get_user(telegram_id)

    if not user:
        return "ar"

    return user["language"]


def add_channel(
    telegram_id,
    channel_id,
    username,
    title
):
    user = get_user(telegram_id)

    if not user:
        create_user(telegram_id)
        user = get_user(telegram_id)

    conn = get_connection()

    conn.execute(
        """
        INSERT INTO channels
        (
            user_id,
            channel_id,
            username,
            title,
            created_at
        )
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(user_id, channel_id)
        DO UPDATE SET
            username = excluded.username,
            title = excluded.title
        """,
        (
            user["id"],
            channel_id,
            username,
            title,
            now()
        )
    )

    conn.commit()
    conn.close()


def get_channels(telegram_id):
    user = get_user(telegram_id)

    if not user:
        return []

    conn = get_connection()

    rows = conn.execute(
        """
        SELECT *
        FROM channels
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (user["id"],)
    ).fetchall()

    conn.close()

    return rows


def get_channel(telegram_id, channel_id):
    user = get_user(telegram_id)

    if not user:
        return None

    conn = get_connection()

    row = conn.execute(
        """
        SELECT *
        FROM channels
        WHERE user_id = ?
        AND channel_id = ?
        """,
        (
            user["id"],
            channel_id
        )
    ).fetchone()

    conn.close()

    return row


def delete_channel(telegram_id, channel_id):
    user = get_user(telegram_id)

    if not user:
        return

    conn = get_connection()

    conn.execute(
        """
        DELETE FROM channels
        WHERE user_id = ?
        AND channel_id = ?
        """,
        (
            user["id"],
            channel_id
        )
    )

    conn.commit()
    conn.close()


def create_post(
    telegram_id,
    channel_id,
    text,
    media_type=None,
    media_path=None,
    buttons="[]",
    status="published"
):
    user = get_user(telegram_id)

    if not user:
        create_user(telegram_id)
        user = get_user(telegram_id)

    conn = get_connection()

    cursor = conn.execute(
        """
        INSERT INTO posts
        (
            user_id,
            channel_id,
            text,
            media_type,
            media_path,
            buttons,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user["id"],
            channel_id,
            text,
            media_type,
            media_path,
            buttons,
            status,
            now()
        )
    )

    post_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return post_id


def get_posts(telegram_id, limit=50):
    user = get_user(telegram_id)

    if not user:
        return []

    conn = get_connection()

    rows = conn.execute(
        """
        SELECT *
        FROM posts
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (
            user["id"],
            limit
        )
    ).fetchall()

    conn.close()

    return rows
