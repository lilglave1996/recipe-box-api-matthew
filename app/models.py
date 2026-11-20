
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


def list_all_recipes():
    db = get_db()

    rows = db.execute(
        "SELECT * FROM recipes ORDER BY id"
    ).fetchall()

    return [dict(row) for row in rows]


def find_recipe(recipe_id):
    db = get_db()

    row = db.execute(
        "SELECT * FROM recipes WHERE id = ?",
        (recipe_id,)
    ).fetchone()

    return dict(row) if row is not None else None


def update_recipe_record(recipe_id, changes):
    db = get_db()

    fields = []
    values = []

    for column in ("title", "ingredients", "instructions", "is_public"):
        if column in changes:
            fields.append(f"{column} = ?")
            values.append(changes[column])

    values.append(recipe_id)

    cur = db.execute(
        f"UPDATE recipes SET {', '.join(fields)} WHERE id = ?",
        values,
    )
    db.commit()

    if cur.rowcount == 0:
        return None

    return find_recipe(recipe_id)


def delete_recipe_record(recipe_id):
    db = get_db()

    db.execute(
        "DELETE FROM recipes WHERE id = ?",
        (recipe_id,),
    )
    db.commit()
