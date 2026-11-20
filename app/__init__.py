
import os

from dotenv import load_dotenv
from flask import Flask, jsonify

from app.db import init_db, close_db

# Load environment variables before importing configuration classes.
load_dotenv()

from config import DevelopmentConfig, TestingConfig, ProductionConfig

JWT_SECRET = os.getenv("JWT_SECRET")

if not JWT_SECRET:
    raise RuntimeError(
        "JWT_SECRET environment variable is required to start the application."
    )


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

    init_db(app)
    app.teardown_appcontext(close_db)

    @app.get("/")
    def hello():
        return jsonify({
            "message": "Recipe Box API",
            "recipes": "/recipes"
        })

    # Import blueprints here to avoid circular imports.
    from app.auth import auth_bp
    from app.recipes import recipes_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(recipes_bp)

    return app
