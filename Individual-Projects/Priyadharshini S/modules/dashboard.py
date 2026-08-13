import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.styling import hero, kpi_card, section_label
from utils.data_gen import generate_incident_timeseries

AMBER = "#F59E0B"
STEEL = "#3B82F6"
GREEN = "#22C55E"
RED = "#F87171"
TEXT = "#E7ECF5"

PLOTLY_TEMPLATE = dict(
    layout=go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT, family="Inter"),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=10, r=10, t=40, b=10),
    )
)


def _style_fig(fig):
    fig.update_layout(PLOTLY_TEMPLATE["layout"])
    fig.update_xaxes(gridcolor="#16233B", zerolinecolor="#16233B")
    fig.update_yaxes(gridcolor="#16233B", zerolinecolor="#16233B")
    return fig


def render(df: pd.DataFrame):
    hero(
        "Executive Dashboard",
        "Real-time portfolio overview across all active construction sites, "
        "powered by predictive analytics and AI-driven risk alerts.",
    )

    total_projects = len(df)
    active = df[df["status"].isin(["In Progress", "Delayed"])].shape[0]
    on_time_pct = round((df["delay_days"] <= 0).mean() * 100, 1)
    total_budget = df["budget"].sum()
    total_actual = df["actual_cost"].sum()
    overrun = (total_actual - total_budget) / total_budget * 100
    safety_score = round(100 - df["safety_incident"].mean() * 100, 1)

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        kpi_card("📁", "Total Projects", f"{total_projects:,}", "8 new this quarter", True)
    with c2:
        kpi_card("🚧", "Active Sites", f"{active:,}", f"{round(active/total_projects*100)}% of portfolio", True)
    with c3:
        kpi_card("⏱️", "On-Time Delivery", f"{on_time_pct}%", "+2.4% vs last qtr", on_time_pct >= 50)
    with c4:
        kpi_card("💰", "Portfolio Budget", f"₹{total_budget/1e7:.1f} Cr",
                  f"{overrun:+.1f}% overrun" if overrun else "on budget", overrun <= 5)
    with c5:
        kpi_card("🦺", "Safety Score", f"{safety_score}/100", "AI monitored", safety_score >= 80)

    st.write("")
    left, right = st.columns([2, 1])

    with left:
        section_label("BUDGET VS ACTUAL COST — BY PROJECT TYPE")
        agg = df.groupby("project_type")[["budget", "actual_cost"]].sum().reset_index()
        agg["budget"] /= 1e7
        agg["actual_cost"] /= 1e7
        fig = go.Figure()
        fig.add_bar(name="Budget (₹ Cr)", x=agg["project_type"], y=agg["budget"], marker_color=STEEL)
        fig.add_bar(name="Actual Cost (₹ Cr)", x=agg["project_type"], y=agg["actual_cost"], marker_color=AMBER)
        fig.update_layout(barmode="group", height=340)
        st.plotly_chart(_style_fig(fig), use_container_width=True)

    with right:
        section_label("PROJECT STATUS SPLIT")
        status_counts = df["status"].value_counts().reset_index()
        status_counts.columns = ["status", "count"]
        fig = px.pie(status_counts, names="status", values="count", hole=0.55,
                     color_discrete_sequence=[AMBER, STEEL, RED, GREEN, "#8CA0BF"])
        fig.update_traces(textinfo="percent+label", textfont_color=TEXT)
        fig.update_layout(height=340, showlegend=False)
        st.plotly_chart(_style_fig(fig), use_container_width=True)

    left2, right2 = st.columns([1.3, 1])

    with left2:
        section_label("SAFETY INCIDENT TREND (24 MONTHS)")
        ts = generate_incident_timeseries()
        fig = go.Figure()
        fig.add_scatter(x=ts["month"], y=ts["near_miss"], name="Near Miss", mode="lines",
                         line=dict(color=STEEL, width=2, dash="dot"))
        fig.add_scatter(x=ts["month"], y=ts["incidents"], name="Incidents", mode="lines+markers",
                         line=dict(color=RED, width=2.5), fill="tozeroy",
                         fillcolor="rgba(248,113,113,0.08)")
        fig.update_layout(height=320, legend=dict(orientation="h", y=1.15))
        st.plotly_chart(_style_fig(fig), use_container_width=True)

    with right2:
        section_label("REGIONAL PROJECT DISTRIBUTION")
        reg = df["region"].value_counts().reset_index()
        reg.columns = ["region", "count"]
        fig = px.bar(reg, x="count", y="region", orientation="h", color="count",
                     color_continuous_scale=["#1E2E4A", AMBER])
        fig.update_layout(height=320, coloraxis_showscale=False)
        st.plotly_chart(_style_fig(fig), use_container_width=True)
