# utils/plotting.py
import plotly.graph_objects as go
import pandas as pd

def plot_yield_curve_surface(df, source_text=""):
    short_col = df.columns[0]
    zmin, zmax = df.values.min(), df.values.max()

    fig = go.Figure()
    fig.add_trace(go.Surface(
        x=df.columns, y=df.index, z=df.values,
        colorscale="ice", reversescale=True,
        cmin=zmin, cmax=zmax,
        hovertemplate="<br>Date: %{y}" "<br>Maturity: %{x}" "<br>Yield: %{z:.2f}%<extra></extra>"
    ))
    fig.add_trace(go.Scatter3d(
        x=[short_col]*len(df), y=df.index, z=df[short_col],
        mode="lines", line=dict(color="black", width=1.5),
        name=f"{short_col} yield"
    ))
    fig.update_layout(
        title="3-D Yield-Curve Surface", height=900,
        scene=dict(
            aspectratio=dict(x=1, y=1.75, z=0.75),
            camera=dict(eye=dict(x=1.65, y=1.57, z=0.25))
        ),
        margin=dict(l=0, r=0, t=40, b=10),
        annotations=[dict(text=source_text, x=0, y=0.02,
                          xref="paper", yref="paper", showarrow=False)]
    )
    return fig

def plot_surface_spread_with_bonds(df_surface: pd.DataFrame,
                                   audit: pd.DataFrame,
                                   title: str,
                                   zmin: float = None,
                                   zmax: float = None):

    cmin = zmin if zmin is not None else audit["SPREAD"].min()
    cmax = zmax if zmax is not None else audit["SPREAD"].max()

    fig = go.Figure()
    fig.add_trace(go.Surface(
        x=df_surface.columns, y=df_surface.index, z=df_surface.values,
        colorscale="RdBu", reversescale=False,
        cmin=cmin, cmax=cmax,
        hovertemplate="<br>Date: %{y}<br>Tenor: %{x}<br>Spread: %{z:.2f} bp<extra></extra>"
    ))
    fig.add_trace(go.Scatter3d(
        x=audit["TENOR_BUCKET"],
        y=audit["OBS_DATE"],
        z=audit["SPREAD"],
        mode="markers",
        marker=dict(size=4, color="black", opacity=0.8),
        text=(audit["id"] + "<br>" +
              audit["CPN_TYP"].fillna("") + " " +
              audit["CPN"].fillna("").astype(str) + "%<br>" +
              "Mat: " + audit["MATURITY"].astype(str)),
        hovertemplate="<b>%{text}</b><br>Date: %{y}<br>Bucket: %{x}" 
                      "<br>Spread: %{z:.2f} bp<extra></extra>",
        name="Spread dots"
    ))

    fig.update_layout(
        title=title, height=900,
        scene=dict(xaxis_title="Tenor bucket", yaxis_title="Obs date",
                   zaxis_title="Spread (bp)",
                   aspectratio=dict(x=1, y=1.75, z=0.75),
                   camera=dict(eye=dict(x=1.6, y=1.6, z=0.25))),
        margin=dict(l=20, r=20, t=40, b=10)
    )
    return fig

def show_summary_table(corp_bonds_df: pd.DataFrame):
    summary_table = corp_bonds_df[[
        "id", "OBS_DATE", "YAS_BOND_YLD", "TENOR_YRS", "DI_YIELD", "SPREAD"
    ]].copy()

    summary_table = summary_table[summary_table["YAS_BOND_YLD"] != 0]

    summary_table["YAS_BOND_YLD"] = summary_table["YAS_BOND_YLD"].round(2)
    summary_table["DI_YIELD"] = summary_table["DI_YIELD"].round(2)
    summary_table["SPREAD"] = summary_table["SPREAD"].round(2)
    summary_table["TENOR_YRS"] = summary_table["TENOR_YRS"].round(2)
    summary_table = summary_table.sort_values(["id", "OBS_DATE"])

    table_fig = go.Figure(data=[go.Table(
        header=dict(
            values=["Bond ID", "Obs Date", "Corp Yield (%)", "Tenor (yrs)", "DI Yield (%)", "Spread (bp)"],
            fill_color="lightgrey",
            align="left"
        ),
        cells=dict(
            values=[
                summary_table["id"],
                summary_table["OBS_DATE"].dt.strftime("%Y-%m-%d"),
                summary_table["YAS_BOND_YLD"],
                summary_table["TENOR_YRS"],
                summary_table["DI_YIELD"],
                summary_table["SPREAD"]
            ],
            align="left"
        )
    )])

    table_fig.update_layout(
        title="Bond Yield vs DI Interpolated Yield and Spread Summary",
        height=600
    )

    return table_fig

def show_di_summary_table(df: pd.DataFrame) -> go.Figure:
    df = df.copy()
    df.index.name = "obs_date"
    df = df.reset_index().melt(id_vars="obs_date", var_name="tenor", value_name="yield")

    df = df.dropna(subset=["yield"])
    df["tenor"] = df["tenor"].astype(str)
    df["yield"] = df["yield"].round(2)

    table = go.Figure(
        data=[go.Table(
            header=dict(values=["Data", "Tenor", "Yield (%)"],
                        fill_color="lightblue", align="left"),
            cells=dict(values=[
                df["obs_date"].dt.strftime("%Y-%m-%d"),
                df["tenor"],
                df["yield"]
            ],
            fill_color="white", align="left"))
        ]
    )
    table.update_layout(
        height=800,
        title="Curva DI Interpolada – Detalhamento por Tenor e Data"
    )
    return table


def show_ipca_summary_table(df: pd.DataFrame) -> go.Figure:
    df = df.copy()
    df.index.name = "obs_date"
    df = df.reset_index().melt(id_vars="obs_date", var_name="tenor", value_name="yield")
    df = df.dropna(subset=["yield"])

    df["tenor"] = df["tenor"].astype(str)
    df["yield"] = df["yield"].round(3)

    table = go.Figure(
        data=[go.Table(
            header=dict(values=["Data", "Tenor (anos)", "Yield (%)"],
                        fill_color="lightgreen", align="left"),
            cells=dict(values=[
                df["obs_date"].dt.strftime("%Y-%m-%d"),
                df["tenor"],
                df["yield"]
            ],
            fill_color="white", align="left"))
        ]
    )
    table.update_layout(
        height=800,
        title="Curva IDxIPCA Interpolada – Por Tenor e Data"
    )
    return table

def show_benchmark_table(df: pd.DataFrame, table_id="benchmarkTable") -> str:
    """
    Gera HTML interativo a partir de um DataFrame de benchmark.
    """
    table_html = df.to_html(index=False, classes="display nowrap", table_id=table_id, border=0)
    return f"""
    <html>
    <head>
        <title>Resumo de Benchmarks por Bond</title>
        <link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
        <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
        <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
        <script>
            $(document).ready(function() {{
                $('#{table_id}').DataTable({{
                    responsive: true,
                    pageLength: 25
                }});
            }});
        </script>
    </head>
    <body>
        <h2>Resumo Final por Bond (DI e IPCA)</h2>
        {table_html}
    </body>
    </html>
    """
