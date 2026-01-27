from database import get_db
from werkzeug.security import generate_password_hash
import uuid

def generate_wallet_hash():
    return f"0x{uuid.uuid4().hex}"

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # -----------------------------
    # USERS TABLE
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        bio TEXT DEFAULT '',
        profile_photo TEXT,
        wallet_hash TEXT
    )
    """)

    # -----------------------------
    # POSTS TABLE
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT,
        media_type TEXT NOT NULL,
        media_path TEXT NOT NULL,
        caption TEXT,
        post_hash TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)

    # -----------------------------
    # POST LIKES TABLE
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS post_likes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        created_at TEXT NOT NULL,
        UNIQUE(post_id, user_id),
        FOREIGN KEY (post_id) REFERENCES posts(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)

    # -----------------------------
    # DEFAULT TEST USER
    # -----------------------------
    cursor.execute(
        "SELECT id FROM users WHERE email = ?",
        ("admin@admin.nl",)
    )

    if cursor.fetchone() is None:
        hashed_password = generate_password_hash("admin")
        cursor.execute(
            """
            INSERT INTO users (username, email, password, bio, profile_photo, wallet_hash)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            ("admin", "admin@admin.nl", hashed_password, "", "default_profile.png", generate_wallet_hash())
        )
        print("Default user created: admin / admin@admin.nl / admin")
    else:
        print("Default user already exists.")

    # -----------------------------
    # TEST USERS
    # -----------------------------
    test_users = [
        ("test1", "test1@test1.nl"),
        ("test2", "test2@test2.nl"),
        ("test3", "test3@test3.nl")
    ]

    hashed_test_password = generate_password_hash("test")

    for username, email in test_users:
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone() is None:
            cursor.execute(
                """
                INSERT INTO users (username, email, password, bio, profile_photo, wallet_hash)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (username, email, hashed_test_password, "", "default_profile.png", generate_wallet_hash())
            )
            print(f"Test user created: {username} / {email} / test")
        else:
            print(f"Test user {username} already exists.")

    conn.commit()
    conn.close()
    print("Database ready.")

if __name__ == "__main__":
    init_db()
