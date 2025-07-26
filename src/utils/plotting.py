# utils/plotting.py
import plotly.graph_objects as go
import pandas as pd

def plot_surface_spread_with_bonds(df_surface: pd.DataFrame,
                                   audit: pd.DataFrame,
                                   title: str,
                                   zmin: float = None,
                                   zmax: float = None):

    cmin = zmin if zmin is not None else audit["SPREAD"].min(),
    cmax = zmax if zmax is not None else audit["SPREAD"].max(),

    fig = go.Figure()
    fig.add_trace(go.Surface(
        x=df_surface.columns, y=df_surface.index, z=df_surface.values,
        colorscale="RdBu", reversescale=False,
        cmin=zmin, cmax=zmax,
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

    table_fig.show()
