# app.py
from flask import Flask, render_template, send_file, request
from routes.filters_routes import filters_blueprint
import pandas as pd

app = Flask(__name__, template_folder="templates")

app.register_blueprint(filters_blueprint)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/summary")
def summary():
    tipo = request.args.get("tipo", "di").lower()
    if tipo not in ["di", "ipca"]:
        tipo = "di"
    chart_path = f"static/{tipo}_summary_table.html"
    return render_template("summary_iframe.html", chart=chart_path, tipo=tipo)

@app.route("/di-surface")
def show_di_surface():
    return render_template("spread_iframe.html", chart="static/di_surface.html", tipo="di")

@app.route("/di-summary")
def di_summary():
    return render_template("summary_iframe.html", chart="static/di_summary_table.html")


@app.route("/wla-surface")
def show_wla_surface():
    return render_template("spread_iframe.html", chart="static/ipca_surface.html", tipo="ipca")

@app.route("/wla-summary")
def show_wla_summary():
    return render_template("summary_iframe.html", chart="static/ipca_summary_table.html")


@app.route("/summary-full")
def summary_full():
    df = pd.read_excel("data/corp_bonds_summary.xlsx")
    return render_template("summary_full.html", summary_data=df.to_dict(orient="records"))


@app.route("/wla-summary-full")
def wla_summary_full():
    with open("static/ipca_summary_table.html") as f:
        content = f.read()
    return render_template("ipca_summary_full.html", table_html=content)


@app.route("/download-summary")
def download_summary():
    return send_file(
        "data/corp_bonds_summary.xlsx",
        download_name="corp_bonds_summary.xlsx",
        as_attachment=True,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@app.route("/spread")
def spread():
    tipo = request.args.get("tipo", "di").lower()
    if tipo not in ["di", "ipca"]:
        tipo = "di"
    chart_path = f"static/{tipo}_spread_surface.html"
    return render_template("spread_iframe.html", chart=chart_path, tipo=tipo)


if __name__ == "__main__":
    app.run(debug=True)
