from datetime import datetime
import os
import uuid

from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from database import get_db
from models.post import Post
from models.user import User

# -----------------------------
# APP SETUP
# -----------------------------
app = Flask(__name__)
app.secret_key = "iets_super_randoms_hier"

# -----------------------------
# FILE STORAGE
# -----------------------------
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
PROFILE_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, "profile")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROFILE_UPLOAD_FOLDER, exist_ok=True)


def generate_wallet_hash():
    # Genereer een pseudo wallet-id voor weergave.
    return f"0x{uuid.uuid4().hex}"


def delete_file_if_exists(relative_path):
    # Verwijder een bestand uit de static-map als het bestaat.
    if not relative_path:
        return
    if relative_path in ("default/default.png", "uploads/default.png", "default.png"):
        return
    base_dir = app.static_folder or os.path.join(os.path.dirname(__file__), "static")
    file_path = relative_path
    if not os.path.isabs(file_path):
        file_path = os.path.join(base_dir, relative_path)
    if os.path.isfile(file_path):
        os.remove(file_path)


def save_profile_photo(profile_photo):
    # Sla een profielfoto op en geef het relative pad terug.
    if not profile_photo or not profile_photo.filename:
        return None
    filename = secure_filename(profile_photo.filename)
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    filepath = os.path.join(PROFILE_UPLOAD_FOLDER, unique_name)
    profile_photo.save(filepath)
    return f"uploads/profile/{unique_name}"


# -----------------------------
# HOME
# -----------------------------
@app.route("/")
def home():
    return render_template("landing.html")


# -----------------------------
# AUTH
# -----------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        profile_photo = request.files.get("profile_photo")

        # Check op bestaande gebruikersnaam en email.
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

        # Hash het wachtwoord en sla de gebruiker op.
        hashed_password = generate_password_hash(password)
        photo_path = save_profile_photo(profile_photo)
        if photo_path is None:
            photo_path = "default/default.png"
        cursor.execute(
            """
            INSERT INTO users (username, email, password, bio, profile_photo, wallet_hash)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (username, email, hashed_password, "", photo_path, generate_wallet_hash())
        )
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Login na registratie.
        session["user_id"] = user_id
        session["user_name"] = username

        return redirect(url_for("profile"))

    return render_template("auth/register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Zoek gebruiker op basis van email.
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user_row = cursor.fetchone()
        conn.close()

        # Check of user bestaat.
        if not user_row:
            flash("Ongeldige inloggegevens.", "danger")
            return redirect(url_for("login"))
        # Map DB-row -> User model (attribute mapping).
        user = User.from_row(user_row)

        if not user.password or not check_password_hash(user.password, password):
            flash("Ongeldige inloggegevens.", "danger")
            return redirect(url_for("login"))

        # Sla user in sessie op.
        session["user_id"] = user.id
        session["user_name"] = user.username

        return redirect(url_for("profile"))

    return render_template("auth/login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


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
    profile_user_row = cursor.fetchone()
    if not profile_user_row:
        conn.close()
        session.clear()
        return redirect(url_for("login"))

    # Map DB-row -> User model (attribute mapping) voor de template.
    profile_user = User.from_row(profile_user_row)
    cursor.execute(
        "SELECT * FROM posts WHERE user_id = ? ORDER BY created_at DESC",
        (session["user_id"],)
    )
    # Map DB-rows -> Post modellen (attribute mapping) voor de template.
    posts = [Post.from_row(row) for row in cursor.fetchall()]
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

    # Haal user op uit db.
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],))
    user_row = cursor.fetchone()

    if not user_row:
        conn.close()
        session.clear()
        return redirect(url_for("login"))
    # Map DB-row -> User model (attribute mapping) voor de form.
    user = User.from_row(user_row)

    # Valideer en update profielgegevens.
    if request.method == "POST":
        new_username = request.form.get("username", "").strip()
        bio = request.form.get("bio", "").strip()
        profile_photo = request.files.get("profile_photo")

        # Username mag niet leeg zijn.
        if not new_username:
            flash("Gebruikersnaam is verplicht.", "danger")
            conn.close()
            return redirect(url_for("edit_profile_page"))

        cursor.execute(
            "SELECT id FROM users WHERE username = ? AND id != ?",
            (new_username, session["user_id"])
        )
        # Username mag niet dubbel zijn.
        if cursor.fetchone():
            flash("Deze gebruikersnaam is al in gebruik.", "danger")
            conn.close()
            return redirect(url_for("edit_profile_page"))

        # Profielfoto vervangen.
        photo_path = user.profile_photo
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
# FEED
# -----------------------------
@app.route("/feed")
def feed():
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Haal alle posts op met gebruikersnaam en like-info.
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            posts.*,
            COALESCE(users.username, 'Onbekende gebruiker') AS username,
            users.wallet_hash AS wallet_hash,
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
    # Map DB-rows -> Post modellen (attribute mapping) voor de feed.
    posts = [Post.from_row(row) for row in cursor.fetchall()]
    conn.close()

    return render_template("feed/feed.html", posts=posts)


# -----------------------------
# POSTS
# -----------------------------
@app.route("/posts/new")
def new_post():
    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("posts/new.html")


@app.route("/posts/create", methods=["POST"])
def create_post():
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Lees het uploadbestand, titel en caption.
    file = request.files.get("media")
    title = request.form.get("title")
    caption = request.form.get("caption")

    if not file or file.filename == "":
        return redirect(url_for("new_post"))

    # Sla bestand op met veilige bestandsnaam.
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # Bepaal mediatype op basis van extensie.
    media_type = "video" if filename.lower().endswith((".mp4", ".mov", ".webm")) else "image"

    # Sla de post op in de database.
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO posts (
            user_id,
            title,
            media_type,
            media_path,
            caption,
            post_hash,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            session["user_id"],
            title,
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

    # Laad de post en controleer toegang.
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
    post_row = cursor.fetchone()

    if not post_row:
        conn.close()
        flash("Post niet gevonden.", "danger")
        return redirect(url_for("profile"))
    # Map DB-row -> Post model (attribute mapping).
    post = Post.from_row(post_row)

    if post.user_id != session["user_id"]:
        conn.close()
        flash("Je kunt deze post niet bewerken.", "danger")
        return redirect(url_for("profile"))

    # Update titel en caption.
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

    # Laad de post en controleer rechten.
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
    post_row = cursor.fetchone()

    if not post_row:
        conn.close()
        flash("Post niet gevonden.", "danger")
        return redirect(url_for("profile"))
    post = Post.from_row(post_row)

    if post.user_id != session["user_id"] and session["user_name"] != "admin":
        conn.close()
        flash("Je kunt deze post niet verwijderen.", "danger")
        return redirect(url_for("profile"))

    # Verwijder likes en post, daarna het bestand.
    media_path = post.media_path
    cursor.execute("DELETE FROM post_likes WHERE post_id = ?", (post_id,))
    cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()

    delete_file_if_exists(media_path)

    flash("Post verwijderd.", "success")
    if request.referrer and "feed" in request.referrer:
        return redirect(url_for("feed"))
    return redirect(url_for("profile"))


@app.route("/posts/<int:post_id>/like", methods=["POST"])
def toggle_like(post_id):
    # Endpoint waar de like-button naartoe POST (zie feed/feed.html).
    if "user_id" not in session:
        return jsonify({"error": "Niet ingelogd."}), 401

    # Controleer of de post bestaat.
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
        # Verwijder de bestaande like (unlike).
        cursor.execute("DELETE FROM post_likes WHERE id = ?", (existing_like["id"],))
        conn.commit()
        cursor.execute(
            "SELECT COUNT(*) AS count FROM post_likes WHERE post_id = ?",
            (post_id,)
        )
        like_count = cursor.fetchone()["count"]
        conn.close()
        # Geef terug: niet geliked + nieuw aantal likes.
        return jsonify({"liked": False, "like_count": like_count})

    # Voeg een like toe.
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
    # Geef terug: geliked + nieuw aantal likes.
    return jsonify({"liked": True, "like_count": like_count})


# -----------------------------
# STATIC PAGES
# -----------------------------
@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/help")
def help_center():
    return render_template("help.html")


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
