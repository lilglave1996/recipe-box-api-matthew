
from sqlalchemy.exc import IntegrityError

from flask import Blueprint, request, jsonify

from app.auth_services import register_user, authenticate_user

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
        return jsonify({
            "error": "username, email, and password are required"
        }), 400

    try:
        user = register_user(
            data["username"],
            data["email"],
            data["password"]
        )
    except IntegrityError:
        return jsonify({
            "error": "username or email already exists"
        }), 409

    return jsonify(user), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({
            "error": "username and password are required"
        }), 400

    user = authenticate_user(username, password)

    if user is None:
        return jsonify({
            "error": "Invalid credentials"
        }), 401

    return jsonify(user), 200
