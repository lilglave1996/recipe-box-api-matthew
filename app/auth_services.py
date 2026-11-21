
import jwt

from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

from app import JWT_SECRET
from sqlalchemy import select
from app.extensions import db
from app.orm_models import User


def register_user(username, email, password):
    password_hash = generate_password_hash(
        password,
        method="pbkdf2:sha256"
    )

    user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        role="user",
    )

    db.session.add(user)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
    }


def authenticate_user(username, password):
    statement = select(User).where(User.username == username)
    user = db.session.scalar(statement)

    if user is None:
        return None

    if not check_password_hash(user.password_hash, password):
        return None

    payload = {
        "sub": str(user.id),
        "exp": datetime.utcnow() + timedelta(hours=1),
        "role": user.role,
    }

    token = jwt.encode(
        payload,
        JWT_SECRET,
        algorithm="HS256"
    )

    return {
        "id": user.id,
        "username": user.username,
        "token": token,
    }
