from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
import uuid
from werkzeug.utils import secure_filename
app = Flask(__name__)
app.secret_key = "iets_super_randoms_hier"



# -----------------------------
# SQLite helper
# -----------------------------
DB_PATH = os.path.join(os.path.dirname(__file__), "app.db")
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # return dict-like rows
    return conn
# -----------------------------
# DEFAULT ROUTES
# -----------------------------
@app.route('/')
def home():
    return render_template("index.html")
@app.route('/verwerk', methods=['POST'])
def verwerk():
    naam = request.form.get("naam")
    return f"Hallo {naam}, dit komt uit de backend!"

# -----------------------------
# REGISTER ROUTE
# -----------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, password)
        )
        conn.commit()
        conn.close()

        # Redirect naar login pagina
        return redirect(url_for('login'))

    return render_template("auth/register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        user = cursor.fetchone()
        conn.close()

        if not user:
            flash("Email bestaat niet.", "danger")
            return redirect(url_for('login'))

        if user['password'] != password:
            flash("Wachtwoord onjuist.", "danger")
            return redirect(url_for('login'))

        session['user_id'] = user['id']
        session['user_name'] = user['name']

        flash(f"Welkom terug, {user['name']}!", "success")
        return redirect(url_for('feed'))  # ✔️ correct

    return render_template("auth/login.html")


@app.route('/feed')
def feed():
    # Check of user is ingelogd
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT posts.id, posts.caption, posts.image_path, posts.created_at, users.name
        FROM posts
        JOIN users ON users.id = posts.user_id
        ORDER BY posts.created_at DESC
        """
    )
    posts = cursor.fetchall()
    conn.close()

    return render_template("posts/feed.html", name=session['user_name'], posts=posts)


@app.route('/upload', methods=['GET', 'POST'])
def upload_post():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        caption = request.form.get("caption", "").strip()
        image_file = request.files.get("image")

        if not image_file or image_file.filename == "":
            flash("Kies een afbeelding om te uploaden.", "danger")
            return redirect(url_for('upload_post'))

        if not allowed_file(image_file.filename):
            flash("Bestandstype niet toegestaan.", "danger")
            return redirect(url_for('upload_post'))

        safe_name = secure_filename(image_file.filename)
        extension = os.path.splitext(safe_name)[1].lower()
        stored_name = f"{uuid.uuid4().hex}{extension}"
        save_path = os.path.join(UPLOAD_FOLDER, stored_name)
        image_file.save(save_path)

        relative_path = os.path.join('uploads', stored_name)

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO posts (user_id, image_path, caption) VALUES (?, ?, ?)",
            (session['user_id'], relative_path, caption)
        )
        conn.commit()
        conn.close()

        flash("Post geplaatst!", "success")
        return redirect(url_for('feed'))

    return render_template("posts/upload.html")

# -----------------------------
# MAIN
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)
