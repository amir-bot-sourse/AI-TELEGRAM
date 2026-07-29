import sqlite3

DB = "database/users.db"


def init_memory():

    conn = sqlite3.connect(DB)

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS memory(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER,

        role TEXT,

        message TEXT

    )
    """)

    conn.commit()

    conn.close()


def save_message(user_id, role, message):

    conn = sqlite3.connect(DB)

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO memory(
            user_id,
            role,
            message
        )
        VALUES(?,?,?)
        """,
        (
            user_id,
            role,
            message
        )
    )

    conn.commit()

    conn.close()


def load_memory(user_id, limit=10):

    conn = sqlite3.connect(DB)

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT role,message
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

    rows = cursor.fetchall()

    conn.close()

    rows.reverse()

    return rows
