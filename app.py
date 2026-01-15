from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import os
from datetime import datetime
import uuid
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

# -----------------------------
# APP SETUP
# -----------------------------
app = Flask(__name__)
app.secret_key = "iets_super_randoms_hier"

# -----------------------------
# DATABASE
# -----------------------------
DB_PATH = os.path.join(os.path.dirname(__file__), "app.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_post_likes_table():
    """Create the post_likes table if it does not exist."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS post_likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(post_id, user_id),
            FOREIGN KEY (post_id) REFERENCES posts(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
    )
    conn.commit()
    conn.close()


ensure_post_likes_table()


def ensure_user_profile_fields():
    """Make sure the users table has profile-related columns and constraints."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
    )
    if cursor.fetchone() is None:
        conn.close()
        return
    cursor.execute("PRAGMA table_info(users)")
    columns = {row["name"] for row in cursor.fetchall()}
    if "bio" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN bio TEXT DEFAULT ''")
    if "profile_photo" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN profile_photo TEXT")
    try:
        cursor.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username ON users(username)"
        )
    except sqlite3.OperationalError:
        # Index creation can fail if duplicate usernames already exist.
        pass
    conn.commit()
    conn.close()


ensure_user_profile_fields()

# -----------------------------
# UPLOAD CONFIG
# -----------------------------
UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
PROFILE_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, "profile_photos")
os.makedirs(PROFILE_UPLOAD_FOLDER, exist_ok=True)


def save_profile_photo(file_storage):
    """Persist a profile photo and return the relative static path."""
    if not file_storage or file_storage.filename == "":
        return None
    filename = secure_filename(file_storage.filename)
    ext = os.path.splitext(filename)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    destination = os.path.join(PROFILE_UPLOAD_FOLDER, unique_name)
    file_storage.save(destination)
    return f"uploads/profile_photos/{unique_name}"


def delete_file_if_exists(relative_path):
    """Remove a static file by relative path if it exists."""
    if not relative_path:
        return
    absolute_path = os.path.join(app.root_path, "static", relative_path)
    if os.path.exists(absolute_path):
        try:
            os.remove(absolute_path)
        except OSError:
            pass

# -----------------------------
# HOME
# -----------------------------
@app.route("/")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return redirect(url_for("feed"))

# -----------------------------
# REGISTER
# -----------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        profile_photo = request.files.get("profile_photo")

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            flash("Gebruikersnaam bestaat al.", "danger")
            return redirect(url_for("register"))

        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            flash("Email bestaat al.", "danger")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)
        photo_path = save_profile_photo(profile_photo)
        cursor.execute(
            """
            INSERT INTO users (username, email, password, bio, profile_photo)
            VALUES (?, ?, ?, ?, ?)
            """,
            (username, email, hashed_password, "", photo_path)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("login"))

    return render_template("auth/register.html")

# -----------------------------
# LOGIN
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if not user or not check_password_hash(user["password"], password):
            flash("Ongeldige inloggegevens.", "danger")
            return redirect(url_for("login"))

        session["user_id"] = user["id"]
        session["user_name"] = user["username"]

        return redirect(url_for("profile"))

    return render_template("auth/login.html")

# -----------------------------
# PROFILE
# -----------------------------
@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],))
    profile_user = cursor.fetchone()
    if not profile_user:
        conn.close()
        session.clear()
        return redirect(url_for("login"))
    cursor.execute(
        "SELECT * FROM posts WHERE user_id = ? ORDER BY created_at DESC",
        (session["user_id"],)
    )
    posts = cursor.fetchall()
    conn.close()

    return render_template(
        "profile/profile.html",
        profile_user=profile_user,
        posts=posts
    )


@app.route("/profile/edit", methods=["GET", "POST"])
def edit_profile_page():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],))
    user = cursor.fetchone()

    if not user:
        conn.close()
        session.clear()
        return redirect(url_for("login"))

    if request.method == "POST":
        new_username = request.form.get("username", "").strip()
        bio = request.form.get("bio", "").strip()
        profile_photo = request.files.get("profile_photo")

        if not new_username:
            flash("Gebruikersnaam is verplicht.", "danger")
            conn.close()
            return redirect(url_for("edit_profile_page"))

        cursor.execute(
            "SELECT id FROM users WHERE username = ? AND id != ?",
            (new_username, session["user_id"])
        )
        if cursor.fetchone():
            flash("Deze gebruikersnaam is al in gebruik.", "danger")
            conn.close()
            return redirect(url_for("edit_profile_page"))

        photo_path = user["profile_photo"]
        if profile_photo and profile_photo.filename:
            delete_file_if_exists(photo_path)
            photo_path = save_profile_photo(profile_photo)

        cursor.execute(
            "UPDATE users SET username = ?, bio = ?, profile_photo = ? WHERE id = ?",
            (new_username, bio, photo_path, session["user_id"])
        )
        conn.commit()
        conn.close()
        session["user_name"] = new_username
        flash("Profiel bijgewerkt.", "success")
        return redirect(url_for("profile"))

    conn.close()
    return render_template("profile/edit_profile.html", user=user)

# -----------------------------
# FEED (ALLE POSTS)
# -----------------------------
@app.route("/feed")
def feed():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            posts.*,
            COALESCE(users.username, 'Onbekende gebruiker') AS username,
            COALESCE(like_counts.like_count, 0) AS like_count,
            CASE WHEN user_likes.user_id IS NULL THEN 0 ELSE 1 END AS liked_by_current_user
        FROM posts
        LEFT JOIN users ON posts.user_id = users.id
        LEFT JOIN (
            SELECT post_id, COUNT(*) AS like_count
            FROM post_likes
            GROUP BY post_id
        ) AS like_counts ON posts.id = like_counts.post_id
        LEFT JOIN post_likes AS user_likes
            ON posts.id = user_likes.post_id AND user_likes.user_id = ?
        ORDER BY posts.created_at DESC
    """, (session["user_id"],))
    posts = cursor.fetchall()
    conn.close()

    return render_template("feed/feed.html", posts=posts)

# -----------------------------
# NEW POST PAGE
# -----------------------------
@app.route("/posts/new")
def new_post():
    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("posts/new.html")

# -----------------------------
# CREATE POST
# -----------------------------
@app.route("/posts/create", methods=["POST"])
def create_post():
    if "user_id" not in session:
        return redirect(url_for("login"))

    file = request.files.get("media")
    caption = request.form.get("caption")

    if not file or file.filename == "":
        return redirect(url_for("new_post"))

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    media_type = "video" if filename.lower().endswith((".mp4", ".mov", ".webm")) else "image"

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO posts (
            user_id,
            media_type,
            media_path,
            caption,
            post_hash,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            session["user_id"],
            media_type,
            f"uploads/{filename}",
            caption,
            None,
            datetime.utcnow().isoformat()
        )
    )
    conn.commit()
    conn.close()

    return redirect(url_for("profile"))


@app.route("/posts/<int:post_id>/edit", methods=["GET", "POST"])
def edit_post(post_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
    post = cursor.fetchone()

    if not post:
        conn.close()
        flash("Post niet gevonden.", "danger")
        return redirect(url_for("profile"))

    if post["user_id"] != session["user_id"]:
        conn.close()
        flash("Je kunt deze post niet bewerken.", "danger")
        return redirect(url_for("profile"))

    if request.method == "POST":
        title = request.form.get("title")
        caption = request.form.get("caption")
        cursor.execute(
            "UPDATE posts SET title = ?, caption = ? WHERE id = ?",
            (title, caption, post_id)
        )
        conn.commit()
        conn.close()
        flash("Post bijgewerkt.", "success")
        return redirect(url_for("profile"))

    conn.close()
    return render_template("posts/edit.html", post=post)


@app.route("/posts/<int:post_id>/delete", methods=["POST"])
def delete_post(post_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
    post = cursor.fetchone()

    if not post:
        conn.close()
        flash("Post niet gevonden.", "danger")
        return redirect(url_for("profile"))

    if post["user_id"] != session["user_id"]:
        conn.close()
        flash("Je kunt deze post niet verwijderen.", "danger")
        return redirect(url_for("profile"))

    media_path = post["media_path"]
    cursor.execute("DELETE FROM post_likes WHERE post_id = ?", (post_id,))
    cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()

    delete_file_if_exists(media_path)

    flash("Post verwijderd.", "success")
    return redirect(url_for("profile"))


@app.route("/posts/<int:post_id>/like", methods=["POST"])
def toggle_like(post_id):
    if "user_id" not in session:
        return jsonify({"error": "Niet ingelogd."}), 401

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM posts WHERE id = ?", (post_id,))
    if cursor.fetchone() is None:
        conn.close()
        return jsonify({"error": "Post niet gevonden."}), 404

    cursor.execute(
        "SELECT id FROM post_likes WHERE post_id = ? AND user_id = ?",
        (post_id, session["user_id"])
    )
    existing_like = cursor.fetchone()

    if existing_like:
        cursor.execute("DELETE FROM post_likes WHERE id = ?", (existing_like["id"],))
        conn.commit()
        cursor.execute(
            "SELECT COUNT(*) AS count FROM post_likes WHERE post_id = ?",
            (post_id,)
        )
        like_count = cursor.fetchone()["count"]
        conn.close()
        return jsonify({"liked": False, "like_count": like_count})

    cursor.execute(
        """
        INSERT INTO post_likes (post_id, user_id, created_at)
        VALUES (?, ?, ?)
        """,
        (post_id, session["user_id"], datetime.utcnow().isoformat())
    )
    conn.commit()
    cursor.execute(
        "SELECT COUNT(*) AS count FROM post_likes WHERE post_id = ?",
        (post_id,)
    )
    like_count = cursor.fetchone()["count"]
    conn.close()
    return jsonify({"liked": True, "like_count": like_count})

# -----------------------------
# LOGOUT
# -----------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
