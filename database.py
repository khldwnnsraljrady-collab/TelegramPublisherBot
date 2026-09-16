import sqlite3
from pathlib import Path
from datetime import datetime, timezone, timedelta


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "publisher.db"


# =========================================================
# CONNECTION
# =========================================================

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def now():
    return datetime.now(timezone.utc).isoformat()


# =========================================================
# INIT DB
# =========================================================

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # -----------------------------------------------------
    # Users
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            language TEXT NOT NULL DEFAULT 'ar',
            created_at TEXT NOT NULL,
            last_active TEXT
        )
    """)

    # -----------------------------------------------------
    # Channels
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # Posts
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            channel_id TEXT NOT NULL,
            message_id INTEGER,
            text TEXT,
            media_type TEXT,
            media_path TEXT,
            buttons TEXT,
            status TEXT NOT NULL DEFAULT 'published',
            created_at TEXT NOT NULL,
            updated_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # -----------------------------------------------------
    # Bot stats
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bot_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER,
            action TEXT NOT NULL,
            details TEXT,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()

    # -----------------------------------------------------
    # Migrations for old DBs
    # -----------------------------------------------------

    _safe_add_column(conn, "users", "last_active", "TEXT")
    _safe_add_column(conn, "posts", "message_id", "INTEGER")
    _safe_add_column(conn, "posts", "updated_at", "TEXT")

    conn.close()


def _safe_add_column(conn, table, column, column_type):
    """Add column if it does not exist (for old databases)."""
    try:
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [row["name"] for row in cursor.fetchall()]

        if column not in columns:
            cursor.execute(
                f"ALTER TABLE {table} ADD COLUMN {column} {column_type}"
            )
            conn.commit()

    except Exception:
        pass


# =========================================================
# USERS
# =========================================================

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
        (telegram_id, language, created_at, last_active)
        VALUES (?, ?, ?, ?)
        """,
        (telegram_id, language, now(), now())
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


def touch_user(telegram_id):
    """Update last_active timestamp."""
    conn = get_connection()

    conn.execute(
        """
        UPDATE users
        SET last_active = ?
        WHERE telegram_id = ?
        """,
        (now(), telegram_id)
    )

    conn.commit()
    conn.close()


def get_all_users(limit=100):
    conn = get_connection()

    rows = conn.execute(
        """
        SELECT *
        FROM users
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,)
    ).fetchall()

    conn.close()
    return rows


def get_active_users(hours=24):
    conn = get_connection()

    since = (
        datetime.now(timezone.utc)
        - timedelta(hours=hours)
    ).isoformat()

    rows = conn.execute(
        """
        SELECT *
        FROM users
        WHERE last_active >= ?
        ORDER BY last_active DESC
        """,
        (since,)
    ).fetchall()

    conn.close()
    return rows


def get_users_count():
    conn = get_connection()

    row = conn.execute(
        "SELECT COUNT(*) as c FROM users"
    ).fetchone()

    conn.close()
    return row["c"] if row else 0


# =========================================================
# CHANNELS
# =========================================================

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


def get_channel_by_id(channel_id):
    """Get channel by channel_id only (any user)."""
    conn = get_connection()

    row = conn.execute(
        """
        SELECT *
        FROM channels
        WHERE channel_id = ?
        """,
        (channel_id,)
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


def get_channels_count():
    conn = get_connection()

    row = conn.execute(
        "SELECT COUNT(*) as c FROM channels"
    ).fetchone()

    conn.close()
    return row["c"] if row else 0


# =========================================================
# POSTS
# =========================================================

def create_post(
    telegram_id,
    channel_id,
    text,
    media_type=None,
    media_path=None,
    buttons="[]",
    status="published",
    message_id=None
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
            message_id,
            text,
            media_type,
            media_path,
            buttons,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user["id"],
            channel_id,
            message_id,
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


def get_post(telegram_id, post_id):
    """Get a single post by id (belongs to user)."""
    user = get_user(telegram_id)

    if not user:
        return None

    conn = get_connection()

    row = conn.execute(
        """
        SELECT *
        FROM posts
        WHERE id = ?
        AND user_id = ?
        """,
        (post_id, user["id"])
    ).fetchone()

    conn.close()
    return row


def update_post_text(telegram_id, post_id, new_text):
    """Update post text and mark updated_at."""
    user = get_user(telegram_id)

    if not user:
        return False

    conn = get_connection()

    cursor = conn.execute(
        """
        UPDATE posts
        SET text = ?, updated_at = ?
        WHERE id = ?
        AND user_id = ?
        """,
        (
            new_text,
            now(),
            post_id,
            user["id"]
        )
    )

    conn.commit()
    changed = cursor.rowcount > 0

    conn.close()
    return changed


def get_posts_count(telegram_id=None):
    conn = get_connection()

    if telegram_id is None:
        row = conn.execute(
            "SELECT COUNT(*) as c FROM posts"
        ).fetchone()
    else:
        user = get_user(telegram_id)

        if not user:
            conn.close()
            return 0

        row = conn.execute(
            "SELECT COUNT(*) as c FROM posts WHERE user_id = ?",
            (user["id"],)
        ).fetchone()

    conn.close()
    return row["c"] if row else 0


# =========================================================
# BOT STATS
# =========================================================

def log_stat(telegram_id, action, details=None):
    """Log an action for admin stats."""
    conn = get_connection()

    conn.execute(
        """
        INSERT INTO bot_stats
        (telegram_id, action, details, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            telegram_id,
            action,
            details,
            now()
        )
    )

    conn.commit()
    conn.close()


def get_bot_stats():
    """Return a dict with main bot statistics."""
    conn = get_connection()

    total_users = conn.execute(
        "SELECT COUNT(*) as c FROM users"
    ).fetchone()["c"]

    total_channels = conn.execute(
        "SELECT COUNT(*) as c FROM channels"
    ).fetchone()["c"]

    total_posts = conn.execute(
        "SELECT COUNT(*) as c FROM posts"
    ).fetchone()["c"]

    # Active in last 24h
    since_24h = (
        datetime.now(timezone.utc)
        - timedelta(hours=24)
    ).isoformat()

    active_24h = conn.execute(
        """
        SELECT COUNT(*) as c
        FROM users
        WHERE last_active >= ?
        """,
        (since_24h,)
    ).fetchone()["c"]

    # Active in last 7 days
    since_7d = (
        datetime.now(timezone.utc)
        - timedelta(days=7)
    ).isoformat()

    active_7d = conn.execute(
        """
        SELECT COUNT(*) as c
        FROM users
        WHERE last_active >= ?
        """,
        (since_7d,)
    ).fetchone()["c"]

    conn.close()

    return {
        "total_users": total_users,
        "total_channels": total_channels,
        "total_posts": total_posts,
        "active_24h": active_24h,
        "active_7d": active_7d,
    }
