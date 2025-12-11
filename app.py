from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from datetime import datetime
from werkzeug.utils import secure_filename

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

# -----------------------------
# UPLOAD CONFIG
# -----------------------------
UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            flash("Email bestaat al.", "danger")
            return redirect(url_for("register"))

        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, password)
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

        if not user or user["password"] != password:
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
    cursor.execute(
        "SELECT * FROM posts WHERE user_id = ? ORDER BY created_at DESC",
        (session["user_id"],)
    )
    posts = cursor.fetchall()
    conn.close()

    return render_template(
        "profile/profile.html",
        username=session["user_name"],
        bio="This is my bio.",
        posts=posts
    )

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
        SELECT posts.*, users.username
        FROM posts
        JOIN users ON posts.user_id = users.id
        ORDER BY posts.created_at DESC
    """)
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
