from flask import Flask, render_template, send_file
from routes.filters_routes import filters_blueprint
import pandas as pd
import os

app = Flask(__name__, template_folder="templates")
app.register_blueprint(filters_blueprint)


# ----------- PÁGINA INICIAL ------------------------
@app.route("/")
def index():
    logs_di = logs_ipca = ""
    try:
        with open("data/logs_di.txt", "r", encoding="utf-8") as f:
            logs_di = f.read()
        with open("data/logs_ipca.txt", "r", encoding="utf-8") as f:
            logs_ipca = f.read()
    except FileNotFoundError:
        logs_di = "⚠️ Logs DI não encontrados."
        logs_ipca = "⚠️ Logs IPCA não encontrados."
    return render_template("index.html", logs_di=logs_di, logs_ipca=logs_ipca)

# ----------- SPREADS SUPERFÍCIE 3D -----------------
@app.route("/spread/<prefixo>")
def spread(prefixo):
    if prefixo not in ["di", "ipca"]:
        prefixo = "di"
    return send_file(f"templates/{prefixo}_spread_surface.html")


# ----------- TABELAS DOS SPREADS ------------------
@app.route("/spread-table/<prefixo>")
def spread_table(prefixo):
    file_map = {
        "di": "summary_DI_table.html",
        "ipca": "summary_IPCA_table.html"
    }
    if prefixo not in file_map:
        prefixo = "di"
    return send_file(f"templates/{file_map[prefixo]}")


# ----------- TABELAS DAS CURVAS INTERPOLADAS ------
@app.route("/summary/<prefixo>")
def summary(prefixo):
    if prefixo == "di":
        return send_file("templates/di_summary_table.html")
    elif prefixo == "ipca":
        return send_file("templates/ipca_summary_table.html")
    else:
        return "Tipo inválido", 400


# ----------- CURVAS DI e IPCA (WLA) ----------------
@app.route("/surface/<prefixo>")
def surface(prefixo):
    if prefixo == "di":
        return send_file("templates/di_surface.html")
    elif prefixo == "ipca":
        return send_file("templates/ipca_surface.html")
    else:
        return "Tipo inválido", 400


# ----------- FULL TABLES (Opcional) ----------------
@app.route("/summary-full")
def summary_full():
    df = pd.read_excel("data/corp_bonds_summary.xlsx")
    return render_template("summary_full.html", summary_data=df.to_dict(orient="records"))


@app.route("/wla-summary-full")
def wla_summary_full():
    with open("templates/ipca_summary_table.html") as f:
        content = f.read()
    return render_template("ipca_summary_full.html", table_html=content)


# ----------- DOWNLOAD DE EXCEL ---------------------
@app.route("/download/<prefixo>")
def download(prefixo):
    if prefixo == "di":
        return send_file(
            "data/corp_bonds_di_summary.xlsx",
            download_name="corp_bonds_di_summary.xlsx",
            as_attachment=True,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    elif prefixo == "ipca":
        return send_file(
            "data/corp_bonds_ipca_summary.xlsx",
            download_name="corp_bonds_ipca_summary.xlsx",
            as_attachment=True,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        return "Tipo inválido", 400

@app.route("/benchmark-summary")
def benchmark_summary():
    return render_template("benchmark_summary_table.html")


if __name__ == "__main__":
    app.run(debug=True)
