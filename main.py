# main.py

from src.utils.file_io import load_inputs
from src.utils.interpolation import interpolate_di_surface
from src.utils.plotting import plot_surface_spread_with_bonds, plot_yield_curve_surface, show_summary_table
from src.core.windowing import build_observation_windows
from src.core.spread_calculator import compute_spreads
from src.config import CONFIG

import pandas as pd
import os

if __name__ == "__main__":
    # 1. Carregar dados
    surface, corp_base, yields_ts = load_inputs(CONFIG)

    # 2. Limpar dados e garantir que há curvas com múltiplos tenores
    surface = surface.dropna(subset=["yield", "tenor"])
    surface = surface[surface["yield"] > 0]

    # Diagnóstico opcional: verificar curvas com múltiplos tenores por data
    curva_por_data = (
        surface.groupby("obs_date")["tenor"]
        .nunique()
        .sort_values(ascending=False)
    )
    print("🧪 Curvas com mais tenores disponíveis:\n", curva_por_data.head())

    # 3. Pivotar a curva para formato wide (um row por data, colunas = tenors)
    pivoted = surface.pivot(index="obs_date", columns="tenor", values="yield").sort_index()

    # 4. Adicionar coluna curve_id (formato: yyyymmdd) para cada linha
    pivoted["curve_id"] = pivoted.index.strftime("%Y%m%d")
    pivoted = pivoted.reset_index().set_index("curve_id")

    # 5. Interpolar a curva DI com os tenores alvo definidos
    yc_table = interpolate_di_surface(surface, CONFIG["TENORS"])

    di_surface = surface.pivot(index="obs_date", columns="tenor", values="yield").sort_index()

    fig_di_surface = plot_yield_curve_surface(
        di_surface,
        source_text="Source: DI B3 – cálculos propios"
    )
    fig_di_surface.write_html("static/di_surface.html")



    # 6. Construir janelas de observação
    obs_windows = build_observation_windows(corp_base, yields_ts, CONFIG["OBS_WINDOW"])

    # 7. Calcular spreads
    corp_bonds, skipped = compute_spreads(corp_base, yields_ts, yc_table, obs_windows, CONFIG["TENORS"])

    # 8. Criar diretórios de saída
    os.makedirs("data", exist_ok=True)
    os.makedirs("static", exist_ok=True)

    # 9. Construir matriz de spreads para gráfico 3D
    spread_surface = corp_bonds.pivot_table(
        index="OBS_DATE",
        columns="TENOR_BUCKET",
        values="SPREAD",
        aggfunc="mean"
    ).sort_index()

    # 10. Ordenar colunas por valor numérico dos tenores
    tenor_order = sorted(CONFIG["TENORS"].items(), key=lambda x: x[1])
    ordered_columns = [k for k, _ in tenor_order if k in spread_surface.columns]
    spread_surface = spread_surface[ordered_columns]

    # 11. Gerar gráfico 3D
    fig = plot_surface_spread_with_bonds(
        df_surface=spread_surface,
        audit=corp_bonds,
        title="Corporate vs. DI Spread Surface (Filtered Universe with Point-in-Time Yields)",
        zmin=-200,
        zmax=2000
    )
    fig.write_html("static/spread_surface.html")

    # 12. Tabela resumo
    table_fig = show_summary_table(corp_bonds)
    if table_fig is not None:
        table_fig.write_html("static/summary_table.html")

    # 13. Exportar observações ignoradas
    pd.DataFrame(skipped, columns=["Bond ID", "Obs Date", "Reason"]).to_csv("data/skipped_yields.csv", index=False)

    print(f"✅ {len(corp_bonds)} spreads calculados. {len(skipped)} observações ignoradas.")