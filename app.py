from flask import Flask, render_template, request
from extensions import db

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///app.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

from models import User

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

if __name__ == '__main__':
    app.run(debug=True)
