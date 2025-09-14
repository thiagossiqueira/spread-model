# main.py
from src.utils.filters import filter_corporate_universe, anomaly_filtering_results
from src.utils.file_io import (
    load_corp_bond_data,
    load_yield_surface,
    load_di_surface,
    load_ipca_surface,
)
from src.utils.interpolation import interpolate_di_surface, interpolate_surface
from src.utils.plotting import (
    plot_surface_spread_with_bonds,
    plot_yield_curve_surface,
    show_summary_table,
    show_di_summary_table,
    show_ipca_summary_table,
    show_benchmark_table
)
from src.core.windowing import build_observation_windows
from src.core.spread_calculator import compute_spreads
from src.config import CONFIG

import pandas as pd
import os

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    os.makedirs("templates", exist_ok=True)

    corp_base_raw = load_corp_bond_data(CONFIG["CORP_PATH"])

    universes = {
        "di": {
            "yields_ts": load_yield_surface(CONFIG["YA_PATH"]),
            "surface": load_di_surface(CONFIG["HIST_CURVE_PATH"]),
            "tenors": CONFIG["TENORS"],
            "inflation_linked": "N",
        },
        "ipca": {
            "yields_ts": load_yield_surface(CONFIG["YA_PATH"]),
            "surface": load_ipca_surface(CONFIG["WLA_CURVE_PATH"]),
            "tenors": CONFIG["WLA_TENORS"],
            "inflation_linked": "Y",
        },
    }

    for tipo, params in universes.items():
        log_path = f"data/logs_{tipo}.txt"
        with open(log_path, "w", encoding="utf-8") as log_file:

            def print_fn(*args, **kwargs):
                print(*args, **kwargs)
                print(*args, **kwargs, file=log_file)

            print_fn(f"\n📊 Processando universo: {tipo.upper()}")

            surface = params["surface"]
            tenors = params["tenors"]
            yields_ts = params["yields_ts"]
            inflation_linked = params["inflation_linked"]

            corp_base = corp_base_raw.copy()
            corp_base = corp_base[corp_base["id"].isin(yields_ts.columns)]

            corp_base = filter_corporate_universe(
                corp_base,
                inflation_linked=inflation_linked,
                log=log_file  # ✅ log opcional para captura no filters.py
            )

            print_fn(f"🧮 Bonds disponíveis após filtro ({tipo}): {len(corp_base)}")

            obs_windows = build_observation_windows(corp_base, yields_ts, CONFIG["OBS_WINDOW"])

            yc_table = (
                interpolate_di_surface(surface, tenors)
                if tipo == "di"
                else interpolate_surface(surface, tenors)
            )

            df_vis = yc_table[[k for k, _ in sorted(tenors.items(), key=lambda x: x[1]) if k in yc_table.columns]]
            df_vis.index.name = "obs_date"

            # Gráfico da curva interpolada
            surface_fig = plot_yield_curve_surface(
                df_vis,
                source_text=f"Source: {'DI' if tipo == 'di' else 'WLA'} B3 – cálculos próprios"
            )
            surface_fig.write_html(f"templates/{tipo}_surface.html")

            # Tabela resumo da curva
            table_func = show_di_summary_table if tipo == "di" else show_ipca_summary_table
            summary_fig = table_func(df_vis)

            if summary_fig is not None:
                title = "Bond Yield vs DI Interpolated Yield and Spread Summary" if tipo == "di" else "Bond Yield vs IPCA Interpolated Yield and Spread Summary"
                path = f"templates/summary_{tipo.upper()}_table.html"

                summary_fig.update_layout(title_text=title)

                summary_fig.write_html(path, include_plotlyjs="cdn", full_html=True)
                print(f"✅ summary_{tipo.upper()}_table.html salvo com sucesso.")
            else:
                print_fn(f"⚠️ {tipo}_summary_table.html não foi gerado.")

            # Calcular spreads
            corp_bonds, skipped = compute_spreads(corp_base, yields_ts, yc_table, obs_windows, tenors)
            print_fn(f"🧮 Spreads calculados ({tipo.upper()}): {len(corp_bonds)} | Ignorados: {len(skipped)}")

            corp_bonds = anomaly_filtering_results(corp_bonds)
            print_fn(f"🧼 Após remover anomalias: {len(corp_bonds)}")

            # Exportar Excel
            df_excel = corp_bonds[["id", "OBS_DATE", "YAS_BOND_YLD", "TENOR_YRS", "DI_YIELD", "SPREAD"]].copy()
            df_excel.columns = ["Bond ID", "Obs Date", "Corp Yield (%)", "Tenor (yrs)", "DI Yield (%)", "Spread (bp)"]
            df_excel.to_excel(f"data/corp_bonds_{tipo}_summary.xlsx", index=False)

            # Superfície de spreads
            spread_surface = corp_bonds.pivot_table(
                index="OBS_DATE",
                columns="TENOR_BUCKET",
                values="SPREAD",
                aggfunc="mean"
            ).sort_index()

            tenor_order = sorted(tenors.items(), key=lambda x: x[1])
            ordered_cols = [k for k, _ in tenor_order if k in spread_surface.columns]
            spread_surface = spread_surface[ordered_cols]

            fig = plot_surface_spread_with_bonds(
                df_surface=spread_surface,
                audit=corp_bonds,
                title=f"Corporate vs. {'DI' if tipo == 'di' else 'IPCA'} Spread Surface (Filtered Universe)",
                zmin=-200,
                zmax=2000,
            )
            fig.write_html(f"templates/{tipo}_spread_surface.html")

            # Tabela resumo geral
            table_fig = show_summary_table(corp_bonds)
            if table_fig is not None:
                table_fig.write_html(f"templates/summary_{tipo.upper()}_table.html")

            # Exportar observações ignoradas
            pd.DataFrame(skipped, columns=["Bond ID", "Obs Date", "Reason"]).to_csv(
                f"data/skipped_{tipo}_yields.csv", index=False
            )

    # 1. Carrega os dois resultados finais
    df_di = pd.read_excel("data/corp_bonds_di_summary.xlsx")[["Bond ID"]].copy()
    df_ipca = pd.read_excel("data/corp_bonds_ipca_summary.xlsx")[["Bond ID"]].copy()

    df_di["Benchmark"] = "DI"
    df_ipca["Benchmark"] = "IPCA"

    df = pd.concat([df_di, df_ipca], axis=0).drop_duplicates()

    # 2. Carrega metadata com múltiplas colunas desejadas
    cols = ["id", "ISSUER", "ULT_PARENT_TICKER_EXCHANGE", "industry_group", "TOT_DEBT_TO_EBITDA", "CIE DES BULK"]
    corp_data = load_corp_bond_data(CONFIG["CORP_PATH"])[cols].copy()

    # 3. Merge com metadados
    df = df.merge(corp_data, left_on="Bond ID", right_on="id", how="left").drop(columns="id")

    # 6. Salva HTML interativo
    html_output = show_benchmark_table(df)
    with open("templates/benchmark_summary_table.html", "w", encoding="utf-8") as f:
        f.write(html_output)

    print("✅ benchmark_summary_table.html gerado com sucesso.")


