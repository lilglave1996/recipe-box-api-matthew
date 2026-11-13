import sqlite3, os, jwt
from functools import wraps

from flask import Flask, g, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
print("Loaded JWT_SECRET:", repr(JWT_SECRET))
DATABASE = "recipes.db"

app = Flask(__name__)

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def recipe_to_dict(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "ingredients": row["ingredients"],
        "instructions": row["instructions"],
        "is_public": bool(row["is_public"]),
    }
def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({"error": "missing Authorization header"}), 401

        parts = auth_header.split(" ", 1)
        if len(parts) != 2 or parts[0] != "Bearer":
            return jsonify({"error": "invalid Authorization header format"}), 401

        token = parts[1]

        try:
            claims = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "token expired, please log in again"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "invalid token"}), 401

        g.current_user_id = claims.get("sub")
        g.current_role = claims.get("role")

        return fn(*args, **kwargs)

    return wrapper

@app.get("/")
def hello():
    return jsonify({"message": "Recipe Box API", "recipes": "/recipes"})

@app.get("/recipes")
def list_recipes():
    rows = get_db().execute("SELECT * FROM recipes ORDER BY id").fetchall()
    return jsonify([recipe_to_dict(r) for r in rows])

@app.get("/recipes/<int:recipe_id>")
def get_recipe(recipe_id):
    row = get_db().execute(
        "SELECT * FROM recipes WHERE id = ?", (recipe_id,)
    ).fetchone()
    if row is None:
        return jsonify({"error": "recipe not found"}), 404
    return jsonify(recipe_to_dict(row))

@app.post("/recipes")
@require_auth
def create_recipe():
    user_id = g.current_user_id  # came from the token

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

@app.post("/register")
def register():
    data = request.get_json(silent=True)

    if (
        not data
        or not data.get("username")
        or not data.get("email")
        or not data.get("password")
    ):
        return jsonify({"error": "username, email, and password are required"}), 400

    password_hash = generate_password_hash(data["password"], method="pbkdf2:sha256")

    db = get_db()
    try:
        cur = db.execute(
            "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
            (data["username"], data["email"], password_hash, "user"),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "username or email already exists"}), 409

    return (
        jsonify(
            {
                "id": cur.lastrowid,
                "username": data["username"],
                "email": data["email"],
            }
        ),
        201,
    )

@app.post("/login")
def login():
    data = request.get_json(silent=True) or {}

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400

    db = get_db()
    user = db.execute(
        "SELECT id, username, password_hash, role FROM users WHERE username = ?",
        (username,),
    ).fetchone()
    
    if user is None or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid credentials"}), 401

    payload = {
        "sub": str(user["id"]),
        "exp": datetime.utcnow() + timedelta(hours=1),
        "role": user["role"],
    }
    
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    return jsonify(
        {
            "id": user["id"],
            "username": user["username"],
            "token": token,
        }
    ), 200

@app.patch("/recipes/<int:recipe_id>")
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

@app.delete("/recipes/<int:recipe_id>")
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

if __name__ == "__main__":
    app.run(debug=True, port=5001)
