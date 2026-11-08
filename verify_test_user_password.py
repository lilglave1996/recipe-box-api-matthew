import sqlite3
from werkzeug.security import check_password_hash

DB_PATH = "recipes.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1. Load the stored hash for testuser
    cur.execute(
        "SELECT password_hash FROM users WHERE username = ?",
        ("testuser",),
    )
    row = cur.fetchone()
    conn.close()

    if row is None:
        print("testuser not found")
        return

    stored_hash = row[0]
    print("Stored hash from DB:", stored_hash)

    # 2. Check a correct and an incorrect candidate
    print("Correct candidate:", check_password_hash(stored_hash, "soup123"))
    print("Wrong candidate:", check_password_hash(stored_hash, "nope123"))

if __name__ == "__main__":
    main()