# main.py

from src.utils.file_io import load_inputs
from src.utils.interpolation import interpolate_di_surface
from src.utils.plotting import plot_surface_spread_with_bonds, show_summary_table
from datos_y_modelos.src.core.windowing import build_observation_windows
from src.core.spread_calculator import compute_spreads
from config import CONFIG

"co"
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

    # Visualizações
    ordered = list(CONFIG["TENORS"].keys())
    fig = plot_surface_spread_with_bonds(yc_table[ordered], corp_bonds,
        "Corporate vs. DI Spread Surface (Filtered Universe with Point-in-Time Yields)")
    fig.show()

    show_summary_table(corp_bonds)

    # Criar diretório de saída se não existir
    os.makedirs("data", exist_ok=True)
    pd.DataFrame(skipped, columns=["Bond ID", "Obs Date", "Reason"]).to_csv("data/skipped_yields.csv", index=False)

    print(f"✅ {len(corp_bonds)} spreads calculados. {len(skipped)} observações ignoradas.")
