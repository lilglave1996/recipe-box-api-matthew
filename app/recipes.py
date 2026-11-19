
import sqlite3

from flask import Blueprint, g, jsonify, request

from app import get_db, recipe_to_dict, require_auth

recipes_bp = Blueprint("recipes", __name__, url_prefix="/recipes")


@recipes_bp.get("")
@require_auth
def list_recipes():
    rows = get_db().execute(
        "SELECT * FROM recipes ORDER BY id"
    ).fetchall()

    return jsonify([recipe_to_dict(r) for r in rows])


@recipes_bp.get("/<int:recipe_id>")
@require_auth
def get_recipe(recipe_id):
    row = get_db().execute(
        "SELECT * FROM recipes WHERE id = ?",
        (recipe_id,)
    ).fetchone()

    if row is None:
        return jsonify({"error": "recipe not found"}), 404

    return jsonify(recipe_to_dict(row))


@recipes_bp.post("")
@require_auth
def create_recipe():
    user_id = g.current_user_id

    data = request.get_json(silent=True)
    if not data or not data.get("title") or not data.get("ingredients"):
        return jsonify({"error": "title and ingredients are required"}), 400

    db = get_db()

    try:
        cur = db.execute(
            "INSERT INTO recipes (title, ingredients, instructions, is_public, owner_id)"
            " VALUES (?, ?, ?, ?, ?)",
            (
                data["title"],
                data["ingredients"],
                data.get("instructions", ""),
                1 if data.get("is_public", True) else 0,
                user_id,
            ),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "a recipe with that title already exists"}), 409

    row = db.execute(
        "SELECT * FROM recipes WHERE id = ?", (cur.lastrowid,)
    ).fetchone()

    return jsonify(recipe_to_dict(row)), 201


@recipes_bp.patch("/<int:recipe_id>")
@require_auth
def update_recipe(recipe_id):
    db = get_db()

    recipe = db.execute(
        "SELECT * FROM recipes WHERE id = ?",
        (recipe_id,)
    ).fetchone()

    if recipe is None:
        return jsonify({"error": "recipe not found"}), 404

    user_id = g.current_user_id
    role = g.current_role

    if recipe["owner_id"] != user_id and role != "admin":
        return jsonify({"error": "you do not have permission to update this recipe"}), 403

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "a JSON body is required"}), 400

    fields, values = [], []

    for column in ("title", "ingredients", "instructions"):
        if column in data:
            fields.append(f"{column} = ?")
            values.append(data[column])

    if "is_public" in data:
        fields.append("is_public = ?")
        values.append(1 if data["is_public"] else 0)

    if not fields:
        return jsonify({"error": "nothing to update"}), 400

    values.append(recipe_id)

    try:
        cur = db.execute(
            f"UPDATE recipes SET {', '.join(fields)} WHERE id = ?", values
        )
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "a recipe with that title already exists"}), 409

    if cur.rowcount == 0:
        return jsonify({"error": "recipe not found"}), 404

    row = db.execute(
        "SELECT * FROM recipes WHERE id = ?", (recipe_id,)
    ).fetchone()

    return jsonify(recipe_to_dict(row))


@recipes_bp.delete("/<int:recipe_id>")
@require_auth
def delete_recipe(recipe_id):
    db = get_db()

    recipe = db.execute(
        "SELECT * FROM recipes WHERE id = ?",
        (recipe_id,)
    ).fetchone()

    if recipe is None:
        return jsonify({"error": "recipe not found"}), 404

    user_id = g.current_user_id
    role = g.current_role

    if recipe["owner_id"] != user_id and role != "admin":
        return jsonify({"error": "you do not have permission to delete this recipe"}), 403

    db.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
    db.commit()

    return "", 204
