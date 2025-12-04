from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)

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
# CRUD ROUTES
# -----------------------------
@app.route('/crud', methods=['GET', 'POST'])
def crud():
    conn = get_db()
    cursor = conn.cursor()
    # Add new item
    if request.method == "POST":
        name = request.form.get("name")
        if name:
            cursor.execute("INSERT INTO items (name) VALUES (?)", (name,))
            conn.commit()
    # Load all items
    cursor.execute("SELECT * FROM items")
    items = cursor.fetchall()
    conn.close()
    return render_template("crud.html", items=items)


@app.route('/crud/update/<int:item_id>', methods=['POST'])
def crud_update(item_id):
    new_name = request.form.get("new_name")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE items SET name=? WHERE id=?", (new_name, item_id))
    conn.commit()
    conn.close()
    return redirect('/crud')


@app.route('/crud/delete/<int:item_id>')
def crud_delete(item_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE id=?", (item_id,))
    conn.commit()
    conn.close()
    return redirect('/crud')

# -----------------------------
# MAIN
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)
