
import sqlite3

from app.db import get_db


def create_user(username, email, password_hash):
    db = get_db()

    try:
        cur = db.execute(
            """
            INSERT INTO users (username, email, password_hash, role)
            VALUES (?, ?, ?, ?)
            """,
            (username, email, password_hash, "user"),
        )
        db.commit()
    except sqlite3.IntegrityError:
        raise

    return cur.lastrowid


def get_user_by_username(username):
    db = get_db()

    return db.execute(
        """
        SELECT id, username, password_hash, role
        FROM users
        WHERE username = ?
        """,
        (username,),
    ).fetchone()
