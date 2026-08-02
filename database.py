import sqlite3
import os

os.makedirs("database", exist_ok=True)

conn = sqlite3.connect(
    "database/users.db",
    check_same_thread=False
)

cursor = conn.cursor()

# =========================
# USERS
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY,
    first_name TEXT,
    username TEXT,
    join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_count INTEGER DEFAULT 0,
    is_vip INTEGER DEFAULT 0,
    is_banned INTEGER DEFAULT 0
)
""")

# =========================
# MEMORY
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS memory(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    message TEXT,
    answer TEXT,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# =========================
# ADMINS
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS admins(
    user_id INTEGER PRIMARY KEY
)
""")

# =========================
# BANNED USERS
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS banned_users(
    user_id INTEGER PRIMARY KEY
)
""")

conn.commit()

# ==========================================================
# USER FUNCTIONS
# ==========================================================

def save_user(user_id, first_name, username):

    cursor.execute(
        """
        INSERT OR IGNORE INTO users
        (user_id, first_name, username)
        VALUES (?, ?, ?)
        """,
        (
            user_id,
            first_name,
            username
        )
    )

    conn.commit()


def update_activity(user_id):

    cursor.execute(
        """
        UPDATE users
        SET last_activity=CURRENT_TIMESTAMP
        WHERE user_id=?
        """,
        (user_id,)
    )

    conn.commit()


def increase_messages(user_id):

    cursor.execute(
        """
        UPDATE users
        SET message_count=message_count+1
        WHERE user_id=?
        """,
        (user_id,)
    )

    conn.commit()


# ==========================================================
# MEMORY FUNCTIONS
# ==========================================================

def save_memory(user_id, message, answer):

    cursor.execute(
        """
        INSERT INTO memory
        (user_id, message, answer)
        VALUES (?, ?, ?)
        """,
        (
            user_id,
            message,
            answer
        )
    )

    conn.commit()


def get_memory(user_id, limit=10):

    cursor.execute(
        """
        SELECT message, answer
        FROM memory
        WHERE user_id=?
        ORDER BY id DESC
        LIMIT ?
        """,
        (
            user_id,
            limit
        )
    )

    return cursor.fetchall()


def clear_memory(user_id):

    cursor.execute(
        """
        DELETE FROM memory
        WHERE user_id=?
        """,
        (user_id,)
    )

    conn.commit()


# ==========================================================
# ADMIN FUNCTIONS
# ==========================================================

def add_admin(user_id):

    cursor.execute(
        """
        INSERT OR IGNORE INTO admins
        VALUES (?)
        """,
        (user_id,)
    )

    conn.commit()


def is_admin(user_id):

    cursor.execute(
        """
        SELECT 1
        FROM admins
        WHERE user_id=?
        """,
        (user_id,)
    )

    return cursor.fetchone() is not None


# ==========================================================
# BAN FUNCTIONS
# ==========================================================

def ban_user(user_id):

    cursor.execute(
        """
        INSERT OR IGNORE INTO banned_users
        VALUES (?)
        """,
        (user_id,)
    )

    conn.commit()


def unban_user(user_id):

    cursor.execute(
        """
        DELETE FROM banned_users
        WHERE user_id=?
        """,
        (user_id,)
    )

    conn.commit()


def is_banned(user_id):

    cursor.execute(
        """
        SELECT 1
        FROM banned_users
        WHERE user_id=?
        """,
        (user_id,)
    )

    return cursor.fetchone() is not None


# ==========================================================
# STATISTICS
# ==========================================================

def get_users_count():

    cursor.execute(
        "SELECT COUNT(*) FROM users"
    )

    return cursor.fetchone()[0]


def get_messages_count():

    cursor.execute(
        "SELECT SUM(message_count) FROM users"
    )

    result = cursor.fetchone()[0]

    return result if result else 0


def get_all_users():

    cursor.execute(
        """
        SELECT user_id, first_name, username
        FROM users
        """
    )

    return cursor.fetchall()
