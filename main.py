# main.py

from src.utils.file_io import load_inputs
from src.utils.interpolation import interpolate_di_surface
from src.utils.plotting import plot_surface_spread_with_bonds, show_summary_table
from src.core.windowing import build_observation_windows
from src.core.spread_calculator import compute_spreads
from config import CONFIG

import pandas as pd
import os

if __name__ == "__main__":
    # Carregar os dados
    surface, corp_base, yields_ts = load_inputs(CONFIG)

    # Interpolação da curva DI
    yc_table = interpolate_di_surface(surface, CONFIG["TENORS"])

    # Janelas de observação para cada título
    obs_windows = build_observation_windows(corp_base, yields_ts, CONFIG["OBS_WINDOW"])

    # Cálculo dos spreads
    corp_bonds, skipped = compute_spreads(corp_base, yields_ts, yc_table, obs_windows, CONFIG["TENORS"])

    # Criar diretórios de saída se não existirem
    os.makedirs("data", exist_ok=True)
    os.makedirs("static", exist_ok=True)

    # Construir matriz de spreads para visualização 3D
    spread_surface = corp_bonds.pivot_table(
        index="OBS_DATE",
        columns="TENOR_BUCKET",
        values="SPREAD"
    ,
    aggfunc="mean"
).sort_index()

    # Garantir que as colunas estejam ordenadas por tenor numérico
    tenor_order = sorted(CONFIG["TENORS"].items(), key=lambda x: x[1])
    ordered_columns = [k for k, _ in tenor_order if k in spread_surface.columns]
    spread_surface = spread_surface[ordered_columns]

    # Gerar gráfico
    fig = plot_surface_spread_with_bonds(
        df_surface=spread_surface,
        audit=corp_bonds,
        title="Corporate vs. DI Spread Surface (Filtered Universe with Point-in-Time Yields)",
        zmin=-200,  # controle manual opcional de escala
        zmax=2000
    )
    # ajustável conforme os spreads típicos
    fig.write_html("static/spread_surface.html")

    # Gerar tabela
    # Gerar tabela
    table_fig = show_summary_table(corp_bonds)
    if table_fig is not None:
            table_fig.write_html("static/summary_table.html")

    # Exportar observações ignoradas
    pd.DataFrame(skipped, columns=["Bond ID", "Obs Date", "Reason"]).to_csv("data/skipped_yields.csv", index=False)

    print(f"✅ {len(corp_bonds)} spreads calculados. {len(skipped)} observações ignoradas.")
