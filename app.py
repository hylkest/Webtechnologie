from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
app = Flask(__name__)
app.secret_key = "iets_super_randoms_hier"



# -----------------------------
# SQLite helper
# -----------------------------
DB_PATH = os.path.join(os.path.dirname(__file__), "app.db")
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

    return render_template("posts/feed.html", name=session['user_name'])

# -----------------------------
# MAIN
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)
