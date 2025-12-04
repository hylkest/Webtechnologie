from flask import Flask, render_template, request, redirect
from extensions import db

app = Flask(__name__)

# --- ROUTES ---
@app.route('/')
def home():
    return render_template("index.html")

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/verwerk', methods=['POST'])
def verwerk():
    naam = request.form.get("naam")
    return f"Hallo {naam}, dit komt uit de backend!"

# --- MAIN ---
if __name__ == '__main__':
    app.run(debug=True)
