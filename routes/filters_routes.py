# routes/filters_routes.py
from flask import Blueprint, render_template, request
import pandas as pd
from src.utils.filters import apply_custom_filters, load_raw_corp_data

filters_blueprint = Blueprint("filters", __name__)

@filters_blueprint.route("/filters", methods=["GET", "POST"])
def filters():
    df_raw = load_raw_corp_data()

    if request.method == "POST":
        inflation = request.form.get("inflation", "N")
        exclude_gov = "exclude_government" in request.form
        exclude_fin = "exclude_financial" in request.form
        cpns = request.form.getlist("cpn")

        df_filtered = apply_custom_filters(df_raw, inflation, exclude_gov, exclude_fin, cpns)
        preview = df_filtered.head(50).to_html(classes="table table-striped", index=False)
        return render_template("filters.html", preview=preview)

    # GET: carregar campos para seleção
    unique_cpns = sorted(df_raw["CPN_TYP"].dropna().unique())
    return render_template("filters.html", unique_cpns=unique_cpns)
