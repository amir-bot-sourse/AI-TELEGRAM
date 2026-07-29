import sqlite3
from datetime import datetime


DB = "database/users.db"


conn = sqlite3.connect(
    DB,
    check_same_thread=False
)

cursor = conn.cursor()


def save_user(user_id, first_name, username):

    cursor.execute(
        """
        INSERT OR IGNORE INTO users
        (
            user_id,
            first_name,
            username
        )
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
        SET last_activity = ?
        WHERE user_id = ?
        """,
        (
            datetime.now(),
            user_id
        )
    )

    conn.commit()



def increase_messages(user_id):

    cursor.execute(
        """
        UPDATE users
        SET message_count = message_count + 1
        WHERE user_id = ?
        """,
        (user_id,)
    )

    conn.commit()



def get_user(user_id):

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE user_id = ?
        """,
        (user_id,)
    )

    return cursor.fetchone()



def get_users_count():

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM users
        """
    )

    return cursor.fetchone()[0]



def get_all_users():

    cursor.execute(
        """
        SELECT *
        FROM users
        ORDER BY join_date DESC
        """
    )

    return cursor.fetchall()
