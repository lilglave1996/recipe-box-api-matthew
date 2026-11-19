
import os

class Config:
    DEBUG = False
    TESTING = False
    DATABASE = os.getenv("DATABASE", "recipes.db")


class DevelopmentConfig(Config):
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    DATABASE = os.getenv("DATABASE", "recipes_dev.db")


class TestingConfig(Config):
    TESTING = True
    DATABASE = os.getenv("DATABASE", "recipes_test.db")


class ProductionConfig(Config):
    DEBUG = False
    DATABASE = os.getenv("DATABASE", "recipes.db")
