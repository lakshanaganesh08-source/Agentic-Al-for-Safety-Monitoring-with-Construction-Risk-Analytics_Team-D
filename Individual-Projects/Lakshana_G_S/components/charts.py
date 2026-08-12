import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# ---------------------------------------------------------
# Budget Chart (Dashboard)
# ---------------------------------------------------------

def budget_chart(project):

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=["Budget", "Actual"],
            y=[
                project["Budget_INR"],
                project["Actual_Cost_INR"]
            ]
        )
    )

    fig.update_layout(
        title="Budget vs Actual Cost",
        height=400,
        template="plotly_white"
    )

    return fig


# ---------------------------------------------------------
# Progress Gauge
# ---------------------------------------------------------

def progress_chart(project):

    fig = go.Figure(go.Indicator(

        mode="gauge+number",

        value=project["Completion_Percentage"],

        title={"text": "Project Completion"},

        gauge={

            "axis": {"range": [0, 100]},

            "bar": {"color": "#2563EB"}

        }

    ))

    fig.update_layout(height=400)

    return fig


# ---------------------------------------------------------
# Cost Breakdown Pie Chart
# ---------------------------------------------------------

def cost_breakdown_chart(result):

    labels = [

        "Material",

        "Labour",

        "Equipment"

    ]

    values = [

        result["Material"],

        result["Labour"],

        result["Equipment"]

    ]

    fig = px.pie(

        names=labels,

        values=values,

        hole=0.55,

        title="Cost Breakdown"

    )

    fig.update_layout(

        template="plotly_white",

        height=450

    )

    return fig


# ---------------------------------------------------------
# Cost Distribution Bar Chart
# ---------------------------------------------------------

def cost_bar_chart(result):

    fig = px.bar(

        x=["Material", "Labour", "Equipment"],

        y=[

            result["Material"],

            result["Labour"],

            result["Equipment"]

        ],

        title="Cost Distribution"

    )

    fig.update_layout(

        template="plotly_white",

        height=450

    )

    return fig




def delay_trend_chart(delay_df):

    df = delay_df.copy()

    df["Date"] = pd.to_datetime(df["Date"])

    monthly = (
        df.groupby(df["Date"].dt.strftime("%b"))
        ["Delay_Days"]
        .sum()
        .reset_index()
    )

    fig = px.line(
        monthly,
        x="Date",
        y="Delay_Days",
        markers=True,
        title="Monthly Delay Trend"
    )

    return fig


def delay_reason_chart(delay_df):

    reasons = (
        delay_df["Reason"]
        .value_counts()
        .reset_index()
    )

    reasons.columns = ["Reason", "Count"]

    fig = px.pie(
        reasons,
        names="Reason",
        values="Count",
        hole=0.45,
        title="Delay Reasons"
    )

    return fig


def severity_chart(delay_df):

    severity = (
        delay_df["Severity"]
        .value_counts()
        .reset_index()
    )

    severity.columns = ["Severity", "Count"]

    fig = px.bar(
        severity,
        x="Severity",
        y="Count",
        color="Severity",
        title="Severity Distribution"
    )

    return fig


def rework_rootcause_chart(df):

    chart = (
        df.groupby("Root_Cause")
        .size()
        .reset_index(name="Count")
    )

    fig = px.pie(
        chart,
        names="Root_Cause",
        values="Count",
        hole=0.55,
        title="Root Cause Distribution"
    )

    fig.update_layout(
        template="plotly_white",
        height=420,
        legend_title="Root Cause"
    )

    return fig


def rework_trade_chart(df):

    chart = (
        df.groupby("Trade")
        .size()
        .reset_index(name="Cases")
        .sort_values("Cases", ascending=False)
    )

    fig = px.bar(
        chart,
        x="Trade",
        y="Cases",
        title="Trade-wise Rework Cases",
        text="Cases"
    )

    fig.update_layout(
        template="plotly_white",
        height=420
    )

    return fig


def rework_trend_chart(df):

    temp = df.copy()

    temp["Date"] = pd.to_datetime(temp["Date"])

    temp["Month"] = temp["Date"].dt.strftime("%b")

    chart = (
        temp.groupby("Month")
        .size()
        .reset_index(name="Cases")
    )

    months = [
        "Jan","Feb","Mar","Apr","May","Jun",
        "Jul","Aug","Sep","Oct","Nov","Dec"
    ]

    chart["Month"] = pd.Categorical(
        chart["Month"],
        months,
        ordered=True
    )

    chart = chart.sort_values("Month")

    fig = px.line(
        chart,
        x="Month",
        y="Cases",
        markers=True,
        title="Monthly Rework Trend"
    )

    fig.update_layout(
        template="plotly_white",
        height=420
    )

    return fig


def rework_status_chart(df):

    chart = (
        df.groupby("Resolved")
        .size()
        .reset_index(name="Count")
    )

    fig = px.pie(
        chart,
        names="Resolved",
        values="Count",
        hole=0.55,
        title="Resolved vs Pending"
    )

    fig.update_layout(
        template="plotly_white",
        height=420
    )

    return fig


def safety_score_chart(df):

    fig = px.histogram(
        df,
        x="Overall_Safety_Score",
        nbins=10,
        title="Safety Score Distribution"
    )

    fig.update_layout(
        template="plotly_white",
        height=420,
        xaxis_title="Safety Score",
        yaxis_title="Inspections"
    )

    return fig


def ppe_chart(df):

    chart = (
        df["PPE_Compliance"]
        .value_counts()
        .reset_index()
    )

    chart.columns = ["PPE", "Count"]

    fig = px.pie(
        chart,
        names="PPE",
        values="Count",
        hole=0.55,
        title="PPE Compliance"
    )

    fig.update_layout(
        template="plotly_white",
        height=420
    )

    return fig


def scaffolding_chart(df):

    chart = (
        df["Scaffolding_Status"]
        .value_counts()
        .reset_index()
    )

    chart.columns = ["Status", "Count"]

    fig = px.bar(
        chart,
        x="Status",
        y="Count",
        text="Count",
        title="Scaffolding Status"
    )

    fig.update_layout(
        template="plotly_white",
        height=420
    )

    return fig


def monthly_safety_chart(df):

    temp = df.copy()

    temp["Inspection_Date"] = pd.to_datetime(
        temp["Inspection_Date"]
    )

    temp["Month"] = temp["Inspection_Date"].dt.strftime("%b")

    chart = (
        temp.groupby("Month")
        .size()
        .reset_index(name="Inspections")
    )

    months = [
        "Jan","Feb","Mar","Apr","May","Jun",
        "Jul","Aug","Sep","Oct","Nov","Dec"
    ]

    chart["Month"] = pd.Categorical(
        chart["Month"],
        months,
        ordered=True
    )

    chart = chart.sort_values("Month")

    fig = px.line(
        chart,
        x="Month",
        y="Inspections",
        markers=True,
        title="Monthly Safety Inspections"
    )

    fig.update_layout(
        template="plotly_white",
        height=420
    )

    return fig

def document_type_chart(df):

    chart = (
        df["Document_Type"]
        .value_counts()
        .reset_index()
    )

    chart.columns = ["Type", "Count"]

    fig = px.pie(
        chart,
        names="Type",
        values="Count",
        hole=0.55,
        title="Document Types"
    )

    fig.update_layout(
        template="plotly_white",
        height=420
    )

    return fig


def document_status_chart(df):

    chart = (
        df["Status"]
        .value_counts()
        .reset_index()
    )

    chart.columns = ["Status", "Count"]

    fig = px.bar(
        chart,
        x="Status",
        y="Count",
        text="Count",
        title="Approval Status"
    )

    fig.update_layout(
        template="plotly_white",
        height=420
    )

    return fig

def document_project_chart(df):

    chart = (
        df.groupby("Project_ID")
        .size()
        .reset_index(name="Documents")
    )

    fig = px.bar(
        chart,
        x="Project_ID",
        y="Documents",
        text="Documents",
        title="Documents by Project"
    )

    fig.update_layout(
        template="plotly_white",
        height=420
    )

    return fig


def document_upload_chart(df):

    temp = df.copy()

    temp["Upload_Date"] = pd.to_datetime(
        temp["Upload_Date"]
    )

    temp["Month"] = temp["Upload_Date"].dt.strftime("%b")

    chart = (
        temp.groupby("Month")
        .size()
        .reset_index(name="Uploads")
    )

    months = [
        "Jan","Feb","Mar","Apr","May","Jun",
        "Jul","Aug","Sep","Oct","Nov","Dec"
    ]

    chart["Month"] = pd.Categorical(
        chart["Month"],
        months,
        ordered=True
    )

    chart = chart.sort_values("Month")

    fig = px.line(
        chart,
        x="Month",
        y="Uploads",
        markers=True,
        title="Monthly Document Uploads"
    )

    fig.update_layout(
        template="plotly_white",
        height=420
    )

    return fig

def workers_chart(df):

    fig = px.histogram(
        df,
        x="Workers_Present",
        nbins=12,
        title="Workers Distribution"
    )

    fig.update_layout(
        template="plotly_white",
        height=420
    )

    return fig

def weather_chart(df):

    chart = (
        df["Weather"]
        .value_counts()
        .reset_index()
    )

    chart.columns = ["Weather","Count"]

    fig = px.pie(
        chart,
        names="Weather",
        values="Count",
        hole=0.55,
        title="Weather Distribution"
    )

    fig.update_layout(
        template="plotly_white",
        height=420
    )

    return fig


def report_trend_chart(df):

    temp = df.copy()

    temp["Date"] = pd.to_datetime(temp["Date"])

    temp["Month"] = temp["Date"].dt.strftime("%b")

    chart = (
        temp.groupby("Month")
        .size()
        .reset_index(name="Reports")
    )

    months = [
        "Jan","Feb","Mar","Apr","May","Jun",
        "Jul","Aug","Sep","Oct","Nov","Dec"
    ]

    chart["Month"] = pd.Categorical(
        chart["Month"],
        categories=months,
        ordered=True
    )

    chart = chart.sort_values("Month")

    fig = px.line(
        chart,
        x="Month",
        y="Reports",
        markers=True,
        title="Monthly Reports"
    )

    fig.update_layout(
        template="plotly_white",
        height=420
    )

    return fig


def supervisor_chart(df):

    chart = (
        df.groupby("Supervisor")
        .size()
        .reset_index(name="Reports")
    )

    fig = px.bar(
        chart,
        x="Supervisor",
        y="Reports",
        text="Reports",
        title="Reports by Supervisor"
    )

    fig.update_layout(
        template="plotly_white",
        height=420
    )

    return fig