import sqlite3
from werkzeug.security import generate_password_hash

DB_PATH = "recipes.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    username = "testuser"
    email = "testuser@example.com"
    password = "soup123"

    password_hash = generate_password_hash(password, method="pbkdf2:sha256")

    cur.execute(
        """
        INSERT INTO users (username, email, password_hash)
        VALUES (?, ?, ?)
        """,
        (username, email, password_hash),
    )

    conn.commit()
    conn.close()
    print("Created test user:", username)
    print("Stored hash:", password_hash)

if __name__ == "__main__":
    main()