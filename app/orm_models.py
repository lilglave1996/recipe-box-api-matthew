from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    password_hash = db.Column(db.Text, nullable=False)
    role = db.Column(
        db.Text,
        nullable=False,
        server_default="user"
    )


class Recipe(db.Model):
    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False, unique=True)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(
        db.Text,
        nullable=False,
        server_default=""
    )
    is_public = db.Column(
        db.Integer,
        nullable=False,
        server_default=db.text("1")
    )
    owner_id = db.Column(db.Text, nullable=True)