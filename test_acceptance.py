
import os
import sqlite3
import tempfile
from datetime import datetime, timedelta, timezone

import jwt

from app import create_app
from app.security import JWT_SECRET


results = []


def check(number, description, response, expected_status, validate_body):
    actual_status = response.status_code
    body = response.get_json(silent=True)

    status_ok = actual_status == expected_status
    body_ok = validate_body(body)

    passed = status_ok and body_ok
    results.append(passed)

    label = "PASS" if passed else "FAIL"

    print(
        f"{number:2}. {label} - {description} | "
        f"expected {expected_status}, actual {actual_status} | "
        f"body: {body!r}"
    )


def has_error(message):
    return lambda body: (
        isinstance(body, dict)
        and body.get("error") == message
    )


with tempfile.TemporaryDirectory() as temp_dir:
    database_path = os.path.join(temp_dir, "acceptance.db")

    app = create_app("testing")
    app.config["DATABASE"] = database_path

    with sqlite3.connect(database_path) as db:
        db.executescript("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user'
            );

            CREATE TABLE recipes (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL UNIQUE,
                ingredients TEXT NOT NULL,
                instructions TEXT NOT NULL DEFAULT '',
                is_public INTEGER NOT NULL DEFAULT 1,
                owner_id INTEGER
            );
        """)

    client = app.test_client()

    owner = {
        "username": "acceptance_owner",
        "email": "owner@example.com",
        "password": "TestPassword123!"
    }

    other = {
        "username": "acceptance_other",
        "email": "other@example.com",
        "password": "TestPassword123!"
    }

    # 1. Welcome endpoint
    response = client.get("/")
    check(
        1, "GET /",
        response, 200,
        lambda body: body == {
            "message": "Recipe Box API",
            "recipes": "/recipes"
        }
    )

    # 2. Successful registration
    response = client.post("/register", json=owner)
    check(
        2, "Register valid user",
        response, 201,
        lambda body: (
            isinstance(body, dict)
            and body.get("username") == owner["username"]
            and body.get("email") == owner["email"]
            and isinstance(body.get("id"), int)
        )
    )

    # 3. Missing registration fields
    response = client.post("/register", json={
        "username": "incomplete"
    })
    check(
        3, "Register missing fields",
        response, 400,
        lambda body: isinstance(body, dict)
        and isinstance(body.get("error"), str)
    )

    # 4. Duplicate registration
    response = client.post("/register", json=owner)
    check(
        4, "Register duplicate user",
        response, 409,
        lambda body: isinstance(body, dict)
        and isinstance(body.get("error"), str)
    )

    # 5. Successful login
    response = client.post("/login", json={
        "username": owner["username"],
        "password": owner["password"]
    })
    check(
        5, "Login valid credentials",
        response, 200,
        lambda body: (
            isinstance(body, dict)
            and body.get("username") == owner["username"]
            and isinstance(body.get("token"), str)
            and isinstance(body.get("id"), int)
        )
    )

    owner_token = (response.get_json() or {}).get("token", "")
    owner_headers = {
        "Authorization": f"Bearer {owner_token}"
    }

    # 6. Missing login credentials
    response = client.post("/login", json={})
    check(
        6, "Login missing credentials",
        response, 400,
        lambda body: isinstance(body, dict)
        and isinstance(body.get("error"), str)
    )

    # 7. Invalid login credentials
    response = client.post("/login", json={
        "username": owner["username"],
        "password": "IncorrectPassword"
    })
    check(
        7, "Login invalid credentials",
        response, 401,
        lambda body: isinstance(body, dict)
        and isinstance(body.get("error"), str)
    )

    # 8. List recipes
    response = client.get("/recipes", headers=owner_headers)
    check(
        8, "List recipes",
        response, 200,
        lambda body: isinstance(body, list)
    )

    # Create a recipe for subsequent tests.
    recipe_data = {
        "title": "Acceptance Test Recipe",
        "ingredients": "Flour, water",
        "instructions": "Mix",
        "is_public": True
    }

    # 11. Create recipe
    response = client.post(
        "/recipes",
        headers=owner_headers,
        json=recipe_data
    )
    check(
        11, "Create recipe",
        response, 201,
        lambda body: (
            isinstance(body, dict)
            and isinstance(body.get("id"), int)
            and body.get("title") == recipe_data["title"]
            and body.get("ingredients") == recipe_data["ingredients"]
            and body.get("instructions") == recipe_data["instructions"]
            and body.get("is_public") is True
        )
    )

    recipe_id = (response.get_json() or {}).get("id", -1)

    # 9. Retrieve existing recipe
    response = client.get(
        f"/recipes/{recipe_id}",
        headers=owner_headers
    )
    check(
        9, "Get existing recipe",
        response, 200,
        lambda body: (
            isinstance(body, dict)
            and body.get("id") == recipe_id
            and body.get("title") == recipe_data["title"]
        )
    )

    # 10. Retrieve nonexistent recipe
    response = client.get(
        "/recipes/999999",
        headers=owner_headers
    )
    check(
        10, "Get nonexistent recipe",
        response, 404,
        has_error("recipe not found")
    )

    # 12. Missing recipe fields
    response = client.post(
        "/recipes",
        headers=owner_headers,
        json={"title": "Incomplete Recipe"}
    )
    check(
        12, "Create missing ingredients",
        response, 400,
        has_error("title and ingredients are required")
    )

    # 13. Duplicate recipe title
    response = client.post(
        "/recipes",
        headers=owner_headers,
        json=recipe_data
    )
    check(
        13, "Create duplicate recipe",
        response, 409,
        has_error("a recipe with that title already exists")
    )

    # 14. Owner updates recipe
    response = client.patch(
        f"/recipes/{recipe_id}",
        headers=owner_headers,
        json={"instructions": "Mix and bake"}
    )
    check(
        14, "Owner updates recipe",
        response, 200,
        lambda body: (
            isinstance(body, dict)
            and body.get("instructions") == "Mix and bake"
            and body.get("id") == recipe_id
        )
    )

    # Register and authenticate a second user.
    client.post("/register", json=other)
    other_login = client.post("/login", json={
        "username": other["username"],
        "password": other["password"]
    })

    other_token = (other_login.get_json() or {}).get("token", "")
    other_headers = {
        "Authorization": f"Bearer {other_token}"
    }

    # 15. Non-owner update forbidden
    response = client.patch(
        f"/recipes/{recipe_id}",
        headers=other_headers,
        json={"title": "Unauthorized Change"}
    )
    check(
        15, "Non-owner update forbidden",
        response, 403,
        has_error("you do not have permission to update this recipe")
    )

    # 16. No valid update fields
    response = client.patch(
        f"/recipes/{recipe_id}",
        headers=owner_headers,
        json={"unknown_field": "value"}
    )
    check(
        16, "No valid update fields",
        response, 400,
        has_error("nothing to update")
    )

    # 18. Non-owner deletion forbidden
    response = client.delete(
        f"/recipes/{recipe_id}",
        headers=other_headers
    )
    check(
        18, "Non-owner delete forbidden",
        response, 403,
        has_error("you do not have permission to delete this recipe")
    )

    # 17. Owner deletes recipe
    response = client.delete(
        f"/recipes/{recipe_id}",
        headers=owner_headers
    )
    check(
        17, "Owner deletes recipe",
        response, 204,
        lambda body: body is None
    )

    # 19. Delete nonexistent recipe
    response = client.delete(
        "/recipes/999999",
        headers=owner_headers
    )
    check(
        19, "Delete nonexistent recipe",
        response, 404,
        has_error("recipe not found")
    )

    # 20. Missing Authorization header
    response = client.get("/recipes")
    check(
        20, "Missing Authorization header",
        response, 401,
        has_error("missing Authorization header")
    )

    # 21. Invalid and expired JWT tokens
    invalid_response = client.get(
        "/recipes",
        headers={"Authorization": "Bearer invalid.token.value"}
    )

    expired_token = jwt.encode(
        {
            "sub": "1",
            "role": "user",
            "exp": datetime.now(timezone.utc) - timedelta(hours=1)
        },
        JWT_SECRET,
        algorithm="HS256"
    )

    expired_response = client.get(
        "/recipes",
        headers={"Authorization": f"Bearer {expired_token}"}
    )

    check(
        21, "Invalid or expired JWT",
        invalid_response, 401,
        lambda body: (
            has_error("invalid token")(body)
            and expired_response.status_code == 401
            and has_error("token expired, please log in again")(
                expired_response.get_json(silent=True)
            )
        )
    )


print("\n" + "=" * 55)
passed = sum(results)
total = len(results)

print(f"ACCEPTANCE RESULT: {passed}/{total} passed")
print("=" * 55)

if total != 21 or passed != 21:
    raise SystemExit(1)
