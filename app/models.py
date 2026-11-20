
from app.db import get_db


def insert_recipe(title, ingredients, instructions, is_public, owner_id):
    db = get_db()

    cur = db.execute(
        "INSERT INTO recipes (title, ingredients, instructions, is_public, owner_id)"
        " VALUES (?, ?, ?, ?, ?)",
        (title, ingredients, instructions, is_public, owner_id),
    )
    db.commit()

    row = db.execute(
        "SELECT * FROM recipes WHERE id = ?",
        (cur.lastrowid,),
    ).fetchone()

    return dict(row)
