# app.py
from flask import Flask, render_template, send_file
from pathlib import Path
from src.config import CONFIG
from src.utils.file_io import load_inputs
from src.core.windowing import build_observation_windows
from src.core.spread_calculator import compute_spreads
from src.utils.interpolation import interpolate_di_surface
import pandas as pd
import io

#surface, corp_base, yields_ts = load_inputs(CONFIG)

df = pd.read_excel("data/corp_bonds_summary.xlsx")

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


@app.route("/summary-full")
def summary_full():
    df = pd.read_excel("data/corp_bonds_summary.xlsx")
    corp_bonds = df  # já está filtrado e renomeado

    return render_template("summary_full.html", summary_data=corp_bonds.to_dict(orient="records"))


@app.route("/wla-summary-full")
def wla_summary_full():
    with open("static/ipca_summary_table.html") as f:
        content = f.read()
    return render_template("ipca_summary_full.html", table_html=content)


@app.route("/download-summary")
def download_summary():
    # Load and prepare data
    surface, corp_base, yields_ts = load_inputs(CONFIG)
    surface = surface.dropna(subset=["yield", "tenor"])
    surface = surface[surface["yield"] > 0]

    if "volume" in surface.columns:
        surface["volume"] = pd.to_numeric(surface["volume"], errors="coerce")
        surface = surface[surface["volume"] > 1000]

    surface = surface.drop_duplicates(subset=["obs_date", "tenor"], keep="last")
    yc_table = interpolate_di_surface(surface, CONFIG["TENORS"])
    obs_windows = build_observation_windows(corp_base, yields_ts, CONFIG["OBS_WINDOW"])
    corp_bonds, _ = compute_spreads(corp_base, yields_ts, yc_table, obs_windows, CONFIG["TENORS"])

    # Filter and format summary
    df = corp_bonds[corp_bonds["YAS_BOND_YLD"] != 0].copy()
    df = df[["id", "OBS_DATE", "YAS_BOND_YLD", "TENOR_YRS", "DI_YIELD", "SPREAD"]]
    df.columns = ["Bond ID", "Obs Date", "Corp Yield (%)", "Tenor (yrs)", "DI Yield (%)", "Spread (bp)"]

    # Write to Excel in-memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="Summary")
    output.seek(0)

    return send_file(
        output,
        download_name="summary_table.xlsx",
        as_attachment=True,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


if __name__ == "__main__":
    app.run(debug=True)