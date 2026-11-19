
import os
import sqlite3
import jwt

from functools import wraps
from datetime import datetime, timedelta
from dotenv import load_dotenv

from flask import Flask, g, jsonify, request, current_app

# Load environment variables before importing configuration classes.
load_dotenv()

from config import DevelopmentConfig, TestingConfig, ProductionConfig

JWT_SECRET = os.getenv("JWT_SECRET")

if not JWT_SECRET:
    raise RuntimeError(
        "JWT_SECRET environment variable is required to start the application."
    )


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


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


def create_app(config_name="development"):
    app = Flask(__name__)

    config_options = {
        "development": DevelopmentConfig,
        "testing": TestingConfig,
        "production": ProductionConfig,
    }

    if config_name not in config_options:
        raise ValueError(f"Unknown configuration: {config_name}")

    app.config.from_object(config_options[config_name])

    app.teardown_appcontext(close_db)

    @app.get("/")
    def hello():
        return jsonify({"message": "Recipe Box API", "recipes": "/recipes"})

    # Import Blueprints here to avoid circular imports.
    from app.auth import auth_bp
    from app.recipes import recipes_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(recipes_bp)

    return app
