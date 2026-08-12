import streamlit as st

from components.cards import metric_card
from components.charts import (
    document_type_chart,
    document_status_chart,
    document_project_chart,
    document_upload_chart
)


def show(data):

    st.title("📄 Construction Document Management")

    st.caption(
        "Manage project documents, approvals, versions and AI document insights."
    )

    st.divider()

    documents = data["documents"]

    # =====================================================
    # FILTERS
    # =====================================================

    c1, c2, c3 = st.columns(3)

    with c1:
        project = st.selectbox(
            "Project",
            ["All"] + sorted(documents["Project_ID"].unique())
        )

    with c2:
        doc_type = st.selectbox(
            "Document Type",
            ["All"] + sorted(documents["Document_Type"].unique())
        )

    with c3:
        status = st.selectbox(
            "Status",
            ["All"] + sorted(documents["Status"].unique())
        )

    df = documents.copy()

    if project != "All":
        df = df[df["Project_ID"] == project]

    if doc_type != "All":
        df = df[df["Document_Type"] == doc_type]

    if status != "All":
        df = df[df["Status"] == status]

    # =====================================================
    # KPI CARDS
    # =====================================================

    total = len(df)

    approved = len(df[df["Status"] == "Approved"])

    pending = len(df[df["Status"] == "Pending Review"])

    latest_version = round(df["Version"].max(), 1)

    st.divider()

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card(
            "Documents",
            total,
            "📄",
            "#2563EB"
        )

    with c2:
        metric_card(
            "Approved",
            approved,
            "✅",
            "#22C55E"
        )

    with c3:
        metric_card(
            "Pending",
            pending,
            "🟡",
            "#F59E0B"
        )

    with c4:
        metric_card(
            "Latest Version",
            latest_version,
            "🆕",
            "#EF4444"
        )

    # =====================================================
    # CHARTS
    # =====================================================

    st.divider()

    left, right = st.columns(2)

    with left:
        st.plotly_chart(
            document_type_chart(df),
            use_container_width=True
        )

    with right:
        st.plotly_chart(
            document_status_chart(df),
            use_container_width=True
        )

    left, right = st.columns(2)

    with left:
        st.plotly_chart(
            document_project_chart(df),
            use_container_width=True
        )

    with right:
        st.plotly_chart(
            document_upload_chart(df),
            use_container_width=True
        )

    # =====================================================
    # AI INSIGHTS
    # =====================================================

    st.divider()

    c1, c2 = st.columns(2)

    with c1:

        st.subheader("🤖 AI Document Insights")

        st.success(
            f"{approved} documents are approved."
        )

        st.warning(
            f"{pending} documents require review."
        )

        st.info(
            "Latest document versions are available."
        )

        st.success(
            "Document repository is synchronized."
        )

    with c2:

        st.subheader("📌 Recommendations")

        st.success("Review pending documents.")

        st.success("Archive superseded files.")

        st.success("Maintain version history.")

        st.success("Verify approval workflow.")

    # =====================================================
    # TABLE
    # =====================================================

    st.divider()

    st.subheader("📋 Document Register")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.caption(
        "📄 ConstructIQ AI Enterprise | Construction Document Management"
    )