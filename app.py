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
    from src.utils.plotting import show_summary_table
    from src.utils.file_io import load_inputs
    surface, _, _ = load_inputs(CONFIG)
    table_fig = show_summary_table(surface)
    return render_template("summary_iframe.html", chart=table_fig.to_html(full_html=False))

if __name__ == "__main__":
    app.run(debug=True)
