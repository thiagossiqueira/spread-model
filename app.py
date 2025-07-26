# app.py
from flask import Flask, render_template
from pathlib import Path

app = Flask(__name__, template_folder="templates")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/spread")
def spread():
    return render_template("spread_iframe.html")

@app.route("/summary")
def summary():
    return render_template("summary_iframe.html")

if __name__ == "__main__":
    app.run(debug=True)