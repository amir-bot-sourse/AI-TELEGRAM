import sqlite3
import os


os.makedirs("database", exist_ok=True)


conn = sqlite3.connect(
    "database/users.db",
    check_same_thread=False
)

cursor = conn.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY,
    first_name TEXT,
    username TEXT,
    join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP,
    message_count INTEGER DEFAULT 0,
    is_vip INTEGER DEFAULT 0,
    is_banned INTEGER DEFAULT 0
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS banned_users(
    user_id INTEGER PRIMARY KEY
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS admins(
    user_id INTEGER PRIMARY KEY
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS memory(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    message TEXT,
    answer TEXT,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")


conn.commit()



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
