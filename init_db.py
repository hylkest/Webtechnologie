from database import get_db

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
        profile_photo TEXT
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
        ("test@test.nl",)
    )

    if cursor.fetchone() is None:
        cursor.execute(
            """
            INSERT INTO users (username, email, password, bio, profile_photo)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("admin", "admin@admin.nl", "admin", "", None)
        )
        print("Default user created: admin / admin@admin.nl / admin")
    else:
        print("Default user already exists.")

    conn.commit()
    conn.close()
    print("Database ready.")

if __name__ == "__main__":
    init_db()
