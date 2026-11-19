
import sqlite3
import jwt

from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from app import get_db, JWT_SECRET

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True)

    if (
        not data
        or not data.get("username")
        or not data.get("email")
        or not data.get("password")
    ):
        return jsonify({"error": "username, email, and password are required"}), 400

    password_hash = generate_password_hash(
        data["password"], method="pbkdf2:sha256"
    )

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


@auth_bp.post("/login")
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
