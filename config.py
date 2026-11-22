import os


class Config:
    DEBUG = False
    TESTING = False
    DATABASE = os.getenv("DATABASE", "recipes.db")
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 60

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    RATELIMIT_ENABLED = True
    RATELIMIT_HEADERS_ENABLED = True


class DevelopmentConfig(Config):
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    DATABASE = os.getenv("DATABASE", "recipes_dev.db")

    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.abspath(DATABASE)}"


class TestingConfig(Config):
    TESTING = True
    DATABASE = "recipes_test.db"

    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.abspath(DATABASE)}"

    RATELIMIT_ENABLED = False


class ProductionConfig(Config):
    DEBUG = False
    DATABASE = os.getenv("DATABASE", "recipes.db")

    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.abspath(DATABASE)}"
