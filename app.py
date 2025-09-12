from flask import Flask, render_template, send_file
from routes.filters_routes import filters_blueprint
import pandas as pd
import os

app = Flask(__name__, template_folder="templates")
app.register_blueprint(filters_blueprint)

@app.route("/")
def index():
    return render_template("index.html")

# ----------- SPREADS SUPERFICIE 3D ---------------------
@app.route("/spread/<prefixo>")
def spread(prefixo):
    if prefixo not in ["di", "ipca"]:
        prefixo = "di"
    return render_template(f"{prefixo}_spread_surface.html")

# ----------- TABELAS DOS SPREADS ---------------------
@app.route("/spread-table/<prefixo>")
def spread_table(prefixo):
    file_map = {
        "di": "summary_DI_table.html",
        "ipca": "summary_IPCA_table.html"
    }
    if prefixo not in file_map:
        prefixo = "di"
    chart_path = f"static/{file_map[prefixo]}"
    return render_template("summary_iframe.html", chart=chart_path, tipo=prefixo)

# ----------- TABELAS DAS CURVAS INTERPOLADAS ----------
@app.route("/summary-table/<prefixo>")
def summary_table(prefixo):
    if prefixo == "di":
        return render_template("summary_DI_table.html")
    elif prefixo == "ipca":
        return render_template("summary_IPCA_table.html")
    else:
        return "Tipo inválido", 400

# ----------- CURVAS DI e IPCA (WLA) -------------------
@app.route("/surface/<prefixo>")
def surface(prefixo):
    if prefixo == "di":
        return render_template("di_surface.html")
    elif prefixo == "ipca":
        return render_template("ipca_surface.html")
    else:
        return "Tipo inválido", 400

# ----------- FULL TABLES (Opcional) --------------------
@app.route("/summary-full")
def summary_full():
    df = pd.read_excel("data/corp_bonds_summary.xlsx")
    return render_template("summary_full.html", summary_data=df.to_dict(orient="records"))

@app.route("/wla-summary-full")
def wla_summary_full():
    with open("static/ipca_summary_table.html") as f:
        content = f.read()
    return render_template("ipca_summary_full.html", table_html=content)

# ----------- DOWNLOAD ------------------------------
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
