
import os
import jwt

from functools import wraps
from flask import g, jsonify, request
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")

if not JWT_SECRET:
    raise RuntimeError(
        "JWT_SECRET environment variable is required to start the application."
    )


def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({
                "error": "missing Authorization header"
            }), 401

        parts = auth_header.split(" ", 1)

        if len(parts) != 2 or parts[0] != "Bearer":
            return jsonify({
                "error": "invalid Authorization header format"
            }), 401

        token = parts[1]

        try:
            claims = jwt.decode(
                token,
                JWT_SECRET,
                algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError:
            return jsonify({
                "error": "token expired, please log in again"
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                "error": "invalid token"
            }), 401

        try:
            g.current_user_id = int(claims["sub"])
        except (KeyError, TypeError, ValueError):
            return jsonify({"error": "invalid token"}), 401


        g.current_role = claims.get("role")

        return fn(*args, **kwargs)

    return wrapper
