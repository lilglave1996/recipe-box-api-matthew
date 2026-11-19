class Config:
    DEBUG = False
    TESTING = False
    DATABASE = "recipes.db"


class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE = "recipes_dev.db"


class TestingConfig(Config):
    TESTING = True
    DATABASE = "recipes_test.db"


class ProductionConfig(Config):
    DATABASE = "recipes.db"