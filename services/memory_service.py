from database import cursor, conn


def save_memory(user_id, message, answer):
    cursor.execute(
        """
        INSERT INTO memory(user_id, message, answer)
        VALUES (?, ?, ?)
        """,
        (
            user_id,
            message,
            answer
        )
    )

    conn.commit()


def load_memory(user_id, limit=10):
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

    rows = cursor.fetchall()

    rows.reverse()

    history = []

    for message, answer in rows:
        history.append(
            {
                "role": "user",
                "content": message
            }
        )

        history.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

    return history
