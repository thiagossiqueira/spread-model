from flask import Flask, render_template, send_file, request
from routes.filters_routes import filters_blueprint
import pandas as pd

app = Flask(__name__, template_folder="templates")
app.register_blueprint(filters_blueprint)


@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/summary")
def summary():
    tipo = request.args.get("tipo", "di").lower()
    if tipo not in ["di", "ipca"]:
        tipo = "di"
    chart_path = f"static/{tipo}_summary_table.html"
    return render_template("summary_iframe.html", chart=chart_path, tipo=tipo)


@app.route("/spread")
def spread():
    tipo = request.args.get("tipo", "di").lower()
    if tipo not in ["di", "ipca"]:
        tipo = "di"
    chart_path = f"static/{tipo}_spread_surface.html"
    return render_template("spread_iframe.html", chart=chart_path, tipo=tipo)


@app.route("/spread-table")
def spread_table():
    tipo = request.args.get("tipo", "di").lower()
    if tipo not in ["di", "ipca"]:
        tipo = "di"
    file_map = {
        "di": "summary_DI_table.html",
        "ipca": "summary_IPCA_table.html"
    }
    chart_path = f"static/{file_map[tipo]}"
    return render_template("summary_iframe.html", chart=chart_path, tipo=tipo)


@app.route("/di-surface")
def di_surface():
    return render_template("spread_iframe.html", chart="static/di_surface.html", tipo="di")


@app.route("/wla-surface")
def wla_surface():
    return render_template("spread_iframe.html", chart="static/ipca_surface.html", tipo="ipca")


@app.route("/download-summary")
def download_summary():
    return send_file(
        "data/corp_bonds_summary.xlsx",
        download_name="corp_bonds_summary.xlsx",
        as_attachment=True,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


if __name__ == "__main__":
    app.run(debug=True)
