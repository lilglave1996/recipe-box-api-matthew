
import sqlite3
from uuid import uuid4

from app import create_app
from app.db import init_db


def run_test():
    test_app = create_app("testing")
    database = test_app.config["DATABASE"]

    assert test_app.config["TESTING"] is True
    assert database == "recipes_test.db"

    init_db(test_app)

    client = test_app.test_client()
    unique = uuid4().hex[:8]

    registration = client.post("/register", json={
        "username": f"testuser_{unique}",
        "email": f"testuser_{unique}@example.com",
        "password": "TestPassword123!"
    })

    print("Registration:", registration.status_code)
    assert registration.status_code == 201

    login = client.post("/login", json={
        "username": f"testuser_{unique}",
        "password": "TestPassword123!"
    })

    print("Login:", login.status_code)
    assert login.status_code == 200

    with sqlite3.connect(database) as db:
        users = db.execute(
            "SELECT COUNT(*) FROM users"
        ).fetchone()[0]

        recipes = db.execute(
            "SELECT COUNT(*) FROM recipes"
        ).fetchone()[0]

    print("Testing database:", database)
    print("Users:", users)
    print("Recipes:", recipes)
    print("Database isolation test passed!")


if __name__ == "__main__":
    run_test()
