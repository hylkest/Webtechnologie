from flask import Flask, render_template, request, redirect
from extensions import db

app = Flask(__name__)

# --- CONFIG ---
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///app.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Import models AFTER db.init_app
from models import User, Item


# --- ROUTES ---
@app.route('/')
def home():
    return render_template("index.html")


@app.route('/verwerk', methods=['POST'])
def verwerk():
    naam = request.form.get("naam")
    return f"Hallo {naam}, dit komt uit de backend!"


@app.route("/profile")
def profile():
    return render_template("profile/profile.html")


# --- CRUD TEST ROUTES ---
@app.route("/crud", methods=["GET", "POST"])
def crud_page():
    if request.method == "POST":
        name = request.form.get("name")
        if name:
            new_item = Item(name=name)
            db.session.add(new_item)
            db.session.commit()

    items = Item.query.all()
    return render_template("test_crud.html", items=items)


@app.route("/crud/delete/<int:item_id>")
def delete_item(item_id):
    item = Item.query.get(item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
    return redirect("/crud")


@app.route("/crud/update/<int:item_id>", methods=["POST"])
def update_item(item_id):
    item = Item.query.get(item_id)
    new_name = request.form.get("new_name")

    if item and new_name:
        item.name = new_name
        db.session.commit()

    return redirect("/crud")


# --- MAIN ---
if __name__ == '__main__':
    app.run(debug=True)
