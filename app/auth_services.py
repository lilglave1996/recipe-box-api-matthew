
import jwt

from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

from app import JWT_SECRET
from app.user_models import create_user, get_user_by_username


def register_user(username, email, password):
    password_hash = generate_password_hash(
        password,
        method="pbkdf2:sha256"
    )

    user_id = create_user(username, email, password_hash)

    return {
        "id": user_id,
        "username": username,
        "email": email,
    }


def authenticate_user(username, password):
    user = get_user_by_username(username)

    if user is None:
        return None

    if not check_password_hash(user["password_hash"], password):
        return None

    payload = {
        "sub": str(user["id"]),
        "exp": datetime.utcnow() + timedelta(hours=1),
        "role": user["role"],
    }

    token = jwt.encode(
        payload,
        JWT_SECRET,
        algorithm="HS256"
    )

    return {
        "id": user["id"],
        "username": user["username"],
        "token": token,
    }
