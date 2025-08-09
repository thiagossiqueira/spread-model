# app.py
from flask import Flask, render_template
from pathlib import Path
from src.config import CONFIG

app = Flask(__name__, template_folder="templates")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/spread")
def spread():
    return render_template("spread_iframe.html", chart="static/spread_surface.html")


@app.route("/summary")
def summary():
    return render_template("summary_iframe.html", chart="static/summary_table.html")


@app.route("/di-surface")
def show_di_surface():
    return render_template("spread_iframe.html", chart="static/di_surface.html")


@app.route("/di-summary")
def di_summary():
    return render_template("summary_iframe.html", chart="static/di_summary_table.html")


@app.route("/wla-surface")
def show_wla_surface():
    return render_template("spread_iframe.html", chart="static/ipca_surface.html")


@app.route("/wla-summary")
def show_wla_summary():
    return render_template("summary_iframe.html", chart="static/ipca_summary_table.html")


if __name__ == "__main__":
    app.run(debug=True)
