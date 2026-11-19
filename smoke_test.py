
import os
import sqlite3
import tempfile

from app import create_app

# Create a temporary database for testing
with tempfile.TemporaryDirectory() as temp_dir:
    database_path = os.path.join(temp_dir, "recipes_test.db")

    app = create_app("testing")
    app.config["DATABASE"] = database_path

    # Create the tables needed by the API
    connection = sqlite3.connect(database_path)

    connection.executescript("""
        CREATE TABLE recipes (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL UNIQUE,
            ingredients TEXT NOT NULL,
            instructions TEXT NOT NULL DEFAULT '',
            is_public INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
        );
    """)

    connection.commit()
    connection.close()

    client = app.test_client()

    # Test 1: Register a user
    register_response = client.post("/register", json={
        "username": "smoketest",
        "email": "smoketest@example.com",
        "password": "TestPassword123!"
    })

    print("Registration:", register_response.status_code)
    print("Registration JSON:", register_response.get_json())

    # Test 2: Log in
    login_response = client.post("/login", json={
        "username": "smoketest",
        "password": "TestPassword123!"
    })

    print("Login:", login_response.status_code)

    login_data = login_response.get_json()
    if login_response.status_code != 200:
        raise RuntimeError(f"Login failed: {login_data}")

    print("Login JSON fields:", list(login_data.keys()))

    # Test 3: List recipes with authentication
    token = login_data["token"]

    recipes_response = client.get(
        "/recipes",
        headers={"Authorization": f"Bearer {token}"}
    )

    print("Recipe listing:", recipes_response.status_code)
    print("Recipe listing JSON:", recipes_response.get_json())

    # Test 4: Verify authentication is required
    unauthorized_response = client.get("/recipes")

    print("Unauthenticated listing:", unauthorized_response.status_code)

    # Verify expected results
    assert register_response.status_code == 201
    assert login_response.status_code == 200
    assert recipes_response.status_code == 200
    assert isinstance(recipes_response.get_json(), list)
    assert unauthorized_response.status_code == 401

    print("\nAll smoke tests passed!")
