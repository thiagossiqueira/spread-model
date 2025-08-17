# main.py
from src.utils.file_io import load_inputs
from src.utils.interpolation import interpolate_di_surface, interpolate_surface

from src.utils.plotting import (
    plot_surface_spread_with_bonds,
    plot_yield_curve_surface,
    show_summary_table,
    show_di_summary_table,
    show_ipca_summary_table
)
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

    # 3. Remover contratos com volume igual a zero
    if "volume" in surface.columns:
        surface["volume"] = pd.to_numeric(surface["volume"], errors="coerce")
        surface = surface[surface["volume"] > 0]

    # Diagnóstico opcional: verificar curvas com múltiplos tenores por data
    curva_por_data = (
        surface.groupby("obs_date")["tenor"]
        .nunique()
        .sort_values(ascending=False)
    )
    print("🧪 Curvas com mais tenores disponíveis:\n", curva_por_data.head())

    # 4. Pivotar a curva para formato wide (um row por data, colunas = tenors)
    surface = surface.drop_duplicates(subset=["obs_date", "tenor"], keep="last")
    pivoted = surface.pivot(index="obs_date", columns="tenor", values="yield").sort_index()

    # 5. Adicionar coluna curve_id (formato: yyyymmdd) para cada linha
    pivoted["curve_id"] = pivoted.index.strftime("%Y%m%d")
    pivoted = pivoted.reset_index().set_index("curve_id")

    # 6. Interpolar a curva DI com os tenores alvo definidos
    yc_table = interpolate_di_surface(surface, CONFIG["TENORS"])

    # 7. Gerar gráfico da superfície DI interpolada (benchmark)
    ordered_cols = [k for k, _ in sorted(CONFIG["TENORS"].items(), key=lambda x: x[1])]
    df_vis = yc_table[ordered_cols] if all(col in yc_table.columns for col in ordered_cols) else yc_table

    fig_di_surface = plot_yield_curve_surface(
        df_vis,
        source_text="Source: DI B3 – cálculos propios"
    )

    print("✅ Salvando gráfico de DI em static/di_surface.html")
    fig_di_surface.write_html("static/di_surface.html")

    # ✅ Salvar tabela DI como HTML (para visualização em /di-summary)
    table_di = show_di_summary_table(df_vis)
    if table_di is not None:
        table_di.write_html("static/di_summary_table.html")

    # 8. Construir janelas de observação
    obs_windows = build_observation_windows(corp_base, yields_ts, CONFIG["OBS_WINDOW"])

    # 9. Calcular spreads
    corp_bonds, skipped = compute_spreads(corp_base, yields_ts, yc_table, obs_windows, CONFIG["TENORS"])

    # 10. Criar diretórios de saída
    os.makedirs("data", exist_ok=True)
    os.makedirs("static", exist_ok=True)

    # 11. Construir matriz de spreads para gráfico 3D
    spread_surface = corp_bonds.pivot_table(
        index="OBS_DATE",
        columns="TENOR_BUCKET",
        values="SPREAD",
        aggfunc="mean"
    ).sort_index()

    # 12. Ordenar colunas por valor numérico dos tenores
    tenor_order = sorted(CONFIG["TENORS"].items(), key=lambda x: x[1])
    ordered_columns = [k for k, _ in tenor_order if k in spread_surface.columns]
    spread_surface = spread_surface[ordered_columns]

    # 13. Gerar gráfico 3D de spreads
    fig = plot_surface_spread_with_bonds(
        df_surface=spread_surface,
        audit=corp_bonds,
        title="Corporate vs. DI Spread Surface (Filtered Universe with Point-in-Time Yields)",
        zmin=-200,
        zmax=2000
    )
    fig.write_html("static/spread_surface.html")

    # 14. Tabela resumo de spreads
    table_fig = show_summary_table(corp_bonds)
    if table_fig is not None:
        table_fig.write_html("static/summary_table.html")





    # 16. Superfície e tabela do contrato ID x IPCA (WLA index)
    ipca_curve = pd.read_excel(
        CONFIG["WLA_CURVE_PATH"],
        sheet_name="only_values"
    )
    ipca_curve["Curve date"] = pd.to_datetime(ipca_curve["Curve date"])
    ipca_surface = ipca_curve.rename(columns={
        "Curve date": "obs_date",
        "Generic ticker": "generic_ticker_id",
        "Term": "tenor",
        "px_last": "yield"
    })
    ipca_surface = ipca_surface.dropna(subset=["yield", "tenor"])
    ipca_surface = ipca_surface[ipca_surface["yield"] > 0]
    ipca_surface["curve_id"] = ipca_surface["generic_ticker_id"] + ipca_surface["obs_date"].dt.strftime("%Y%m%d")
    ipca_surface = ipca_surface.drop_duplicates(subset=["curve_id"], keep="last")

    ipca_interp = interpolate_surface(ipca_surface, CONFIG["WLA_TENORS"])
    ipca_ordered = [k for k, _ in sorted(CONFIG["WLA_TENORS"].items(), key=lambda x: x[1])]
    df_ipca_vis = ipca_interp[ipca_ordered] if all(c in ipca_interp.columns for c in ipca_ordered) else ipca_interp

    fig_ipca_surface = plot_yield_curve_surface(df_ipca_vis, source_text="Source: WLA B3 – cálculos próprios")
    fig_ipca_surface.write_html("static/ipca_surface.html")

    fig_ipca_table = show_ipca_summary_table(ipca_surface)
    fig_ipca_table.write_html("static/ipca_summary_table.html")

    # 17. Exportar observações ignoradas
    pd.DataFrame(skipped, columns=["Bond ID", "Obs Date", "Reason"]).to_csv("data/skipped_yields.csv", index=False)

    print(f"✅ {len(corp_bonds)} spreads calculados. {len(skipped)} observações ignoradas.")