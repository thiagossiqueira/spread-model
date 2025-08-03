# main.py

from src.utils.file_io import load_inputs
from src.utils.interpolation import interpolate_di_surface
from src.utils.plotting import plot_surface_spread_with_bonds, show_summary_table
from src.core.windowing import build_observation_windows
from src.core.spread_calculator import compute_spreads
from src.config import CONFIG

import pandas as pd
import os

if __name__ == "__main__":
    # 1. Carregar dados
    surface, corp_base, yields_ts = load_inputs(CONFIG)

    # 2. Gera curve_id se ainda não existir
    if "curve_id" not in surface.columns:
        surface["curve_id"] = surface["generic_ticker_id"] + surface["obs_date"].dt.strftime("%Y%m%d")

    # 3. Interpolação da curva DI (mantendo formato longo)
    yc_table = interpolate_di_surface(surface, CONFIG["TENORS"]).set_index("curve_id")

    # 4. Construir janelas de observação
    obs_windows = build_observation_windows(corp_base, yields_ts, CONFIG["OBS_WINDOW"])

    # 5. Calcular spreads
    corp_bonds, skipped = compute_spreads(corp_base, yields_ts, yc_table, obs_windows, CONFIG["TENORS"])

    # 6. Criar diretórios de saída
    os.makedirs("data", exist_ok=True)
    os.makedirs("static", exist_ok=True)

    # 7. Construir matriz 3D de spreads
    spread_surface = corp_bonds.pivot_table(
        index="OBS_DATE",
        columns="TENOR_BUCKET",
        values="SPREAD",
        aggfunc="mean"
    ).sort_index()

    # Ordenar colunas numericamente
    tenor_order = sorted(CONFIG["TENORS"].items(), key=lambda x: x[1])
    ordered_columns = [k for k, _ in tenor_order if k in spread_surface.columns]
    spread_surface = spread_surface[ordered_columns]

    # 8. Gerar gráfico 3D
    fig = plot_surface_spread_with_bonds(
        df_surface=spread_surface,
        audit=corp_bonds,
        title="Corporate vs. DI Spread Surface (Filtered Universe with Point-in-Time Yields)",
        zmin=-200,
        zmax=2000
    )
    fig.write_html("static/spread_surface.html")

    # 9. Tabela resumo
    table_fig = show_summary_table(corp_bonds)
    if table_fig is not None:
        table_fig.write_html("static/summary_table.html")

    # 10. Exportar observações ignoradas
    pd.DataFrame(skipped, columns=["Bond ID", "Obs Date", "Reason"]).to_csv("data/skipped_yields.csv", index=False)

    print(f"✅ {len(corp_bonds)} spreads calculados. {len(skipped)} observações ignoradas.")
