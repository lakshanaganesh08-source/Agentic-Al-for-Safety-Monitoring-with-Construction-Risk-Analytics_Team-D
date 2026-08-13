"""
Project Management Module for Construction Intelligence Hub.

Provides complete project lifecycle management: Project Creation, Task Tracking,
Progress & Health Calculation, Schedule Comparison, Budget Tracking (in INR ₹),
Milestone Control, Risk/Issue Tracking, and Project Summary Export.

All project data is strictly scoped per project ID and stored in SQLite.
"""

from __future__ import annotations

import datetime
import pandas as pd
import streamlit as st

from database import models
from database.db import get_db
from utils.styling import page_hero, stat_card


def _format_inr(val: float) -> str:
    """Format currency values in Indian Rupee standard (Crores, Lakhs, or Thousands)."""
    if val is None:
        return "₹0"
    val = float(val)
    abs_val = abs(val)
    sign = "-" if val < 0 else ""
    if abs_val >= 10_000_000:
        return f"{sign}₹{abs_val / 10_000_000:.2f} Cr"
    elif abs_val >= 100_000:
        return f"{sign}₹{abs_val / 100_000:.2f} Lakhs"
    else:
        return f"{sign}₹{abs_val:,.0f}"


def _compute_project_health(
    project: dict, tasks: list[dict], issues: list[dict]
) -> tuple[str, str, str]:
    """
    Compute real construction project health status:
    - ON TRACK (Green)
    - AT RISK (Yellow)
    - DELAYED (Red)
    """
    progress = float(project.get("progress") or 0.0)
    status = project.get("status", "In Progress")
    budget = float(project.get("budget") or 0.0)
    spending = float(project.get("actual_spending") or 0.0)

    if status == "Completed" or progress >= 100.0:
        return "ON TRACK", "#00E676", "✅ Project completed successfully."

    today_str = datetime.date.today().isoformat()
    end_date = project.get("end_date")

    delayed_tasks = [
        t for t in tasks if t.get("status") == "Delayed" or (
            t.get("due_date") and t.get("due_date") < today_str and t.get("status") != "Completed"
        )
    ]
    critical_issues = [
        i for i in issues if i.get("status") != "Resolved" and i.get("severity") in ("High", "Critical")
    ]

    budget_util = (spending / budget * 100) if budget > 0 else 0.0

    if (end_date and end_date < today_str and progress < 100.0) or len(delayed_tasks) >= 2:
        return "DELAYED", "#FF5252", f"🔴 Behind schedule. {len(delayed_tasks)} delayed task(s)."
    elif budget_util > 95.0 or len(critical_issues) > 0 or len(delayed_tasks) == 1:
        return "AT RISK", "#FFAB00", f"🟡 Warning: Budget utilization at {budget_util:.1f}% or open critical issues."
    else:
        return "ON TRACK", "#00E676", "🟢 Progress on schedule within allocated budget."


def render():
    page_hero(
        "📋", "Project Task Management",
        "Track, Filter, and Manage Site Operations &amp; Work Assignments",
        badge="OPERATIONS CONTROL"
    )

    with get_db() as conn:
        projects = models.list_projects(conn)

    if not projects:
        with get_db() as conn:
            p_id = models.create_project(
                conn,
                name="Executive Tower Construction",
                client_name="Metro Corp",
                location="Bengaluru, KA",
                project_type="Commercial",
                status="In Progress",
                budget=50_000_000,
                actual_spending=32_000_000,
                start_date="2025-01-01",
                end_date="2025-12-31",
                progress=64.0,
            )
            projects = models.list_projects(conn)

    project_options = {f"{p['id']}: {p['name']} ({p.get('status', 'Active')})": p["id"] for p in projects}

    # Top Control Bar: Project Selector & New Project Expander
    col_sel, col_new = st.columns([3, 1])
    with col_sel:
        selected_label = st.selectbox(
            "🏗️ Active Project Selection",
            options=list(project_options.keys()),
            index=0,
            key="pm_project_selector",
        )
        selected_project_id = project_options[selected_label]
    with col_new:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        show_new_proj = st.button("➕ Create New Project", use_container_width=True)

    if show_new_proj or st.session_state.get("pm_toggle_new_proj"):
        st.session_state.pm_toggle_new_proj = True
        with st.expander("🏗️ Create New Construction Project", expanded=True):
            with st.form("create_project_form"):
                p_name = st.text_input("Project Name *", placeholder="e.g. Skyline Residency Phase 2")
                c1, c2, c3 = st.columns(3)
                with c1:
                    p_client = st.text_input("Client Name", placeholder="e.g. Apex Infra Pvt Ltd")
                    p_type = st.selectbox("Project Type", ["Commercial", "Residential", "Infrastructure", "Industrial"])
                with c2:
                    p_loc = st.text_input("Location", placeholder="e.g. Mumbai, MH")
                    p_status = st.selectbox("Status", ["Planning", "In Progress", "On Hold", "Completed", "Cancelled"], index=1)
                with c3:
                    p_pm = st.text_input("Project Manager", placeholder="e.g. Rajesh Kumar")
                    p_budget = st.number_input("Estimated Budget (INR ₹)", min_value=0.0, value=10000000.0, step=500000.0)

                d1, d2 = st.columns(2)
                with d1:
                    p_start = st.date_input("Start Date", value=datetime.date.today())
                with d2:
                    p_end = st.date_input("Expected Completion Date", value=datetime.date.today() + datetime.timedelta(days=180))

                p_desc = st.text_area("Description / Scope of Work", placeholder="Brief details about structural scope...")

                submit_proj = st.form_submit_button("🚀 Save Project", type="primary", use_container_width=True)

                if submit_proj:
                    if not p_name.strip():
                        st.error("Project Name is required.")
                    elif p_end < p_start:
                        st.error("Expected Completion Date cannot be earlier than Start Date.")
                    else:
                        with get_db() as conn:
                            new_id = models.create_project(
                                conn,
                                name=p_name.strip(),
                                client_name=p_client.strip(),
                                location=p_loc.strip(),
                                project_type=p_type,
                                status=p_status,
                                budget=p_budget,
                                actual_spending=0.0,
                                start_date=p_start.isoformat(),
                                end_date=p_end.isoformat(),
                                project_manager=p_pm.strip(),
                                description=p_desc.strip(),
                                progress=0.0,
                            )
                        st.session_state.pm_toggle_new_proj = False
                        st.success(f"✅ Project '{p_name}' created successfully (ID: #{new_id})!")
                        st.rerun()

    # Load Active Project Data
    with get_db() as conn:
        active_project = models.get_project_by_id(conn, selected_project_id)
        tasks = models.list_tasks(conn, selected_project_id)
        milestones = models.list_milestones(conn, selected_project_id)
        issues = models.list_project_issues(conn, selected_project_id)

    if not active_project:
        st.error("Project not found.")
        return

    health_title, health_color, health_desc = _compute_project_health(active_project, tasks, issues)

    # ---------------- 📊 PROJECT EXECUTIVE STAT CARDS ----------------
    tot_tasks = len(tasks)
    completed_cnt = sum(1 for t in tasks if t["status"] == "Completed")
    in_prog_cnt = sum(1 for t in tasks if t["status"] == "In Progress")
    pending_cnt = sum(1 for t in tasks if t["status"] in ("Pending", "Not Started", "Delayed"))

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(stat_card("📌", "Total Tasks", str(tot_tasks), None, "#F0F6FC"), unsafe_allow_html=True)
    with c2:
        st.markdown(stat_card("✅", "Completed Tasks", str(completed_cnt), None, "#00E676"), unsafe_allow_html=True)
    with c3:
        st.markdown(stat_card("🔄", "In Progress", str(in_prog_cnt), None, "#00E5FF"), unsafe_allow_html=True)
    with c4:
        st.markdown(stat_card("⏳", "Pending / Delayed", str(pending_cnt), None, "#FFAB00"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------- 🏗️ PROJECT OVERVIEW & METRICS ----------------
    ov1, ov2 = st.columns([1.6, 1])
    with ov1:
        st.markdown(f"""
            <div class="hub-card" style="padding: 20px; margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <h3 style="margin: 0; color: #FFFFFF;">🏗️ {active_project['name']}</h3>
                    <span class="hub-pill" style="background: {health_color}22; color: {health_color}; border: 1px solid {health_color}55;">
                        ● {health_title}
                    </span>
                </div>
                <p style="color: #9BA6B4; font-size: 0.9rem; margin-bottom: 16px;">
                    <b>Client:</b> {active_project.get('client_name') or 'N/A'} &nbsp;|&nbsp;
                    <b>Location:</b> {active_project.get('location') or 'N/A'} &nbsp;|&nbsp;
                    <b>Manager:</b> {active_project.get('project_manager') or 'N/A'} &nbsp;|&nbsp;
                    <b>Type:</b> {active_project.get('project_type') or 'Commercial'}
                </p>
                <div style="margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; color: #C9D1D9; font-size: 0.88rem; font-weight: 600; margin-bottom: 4px;">
                        <span>Overall Project Progress</span>
                        <span>{active_project.get('progress', 0.0):.1f}%</span>
                    </div>
                    <div style="background: rgba(255,255,255,0.1); border-radius: 999px; height: 10px; overflow: hidden;">
                        <div style="background: linear-gradient(90deg, #00E5FF, #00E676); width: {min(100.0, max(0.0, active_project.get('progress', 0.0)))}%; height: 100%;"></div>
                    </div>
                </div>
                <p style="color: #8B949E; font-size: 0.82rem; margin: 12px 0 0 0;">{health_desc}</p>
            </div>
        """, unsafe_allow_html=True)

    with ov2:
        budget_est = float(active_project.get("budget") or 0.0)
        spending = float(active_project.get("actual_spending") or 0.0)
        remaining = budget_est - spending
        util = (spending / budget_est * 100) if budget_est > 0 else 0.0

        st.markdown(f"""
            <div class="hub-card" style="padding: 20px; margin-bottom: 20px;">
                <h4 style="margin: 0 0 12px 0; color: #00E5FF;">💰 Financial Budget Summary</h4>
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 0.88rem;">
                    <span style="color: #8B949E;">Estimated Budget:</span>
                    <span style="color: #F0F6FC; font-weight: 700;">{_format_inr(budget_est)}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 0.88rem;">
                    <span style="color: #8B949E;">Actual Spending:</span>
                    <span style="color: #00E5FF; font-weight: 700;">{_format_inr(spending)}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 12px; font-size: 0.88rem;">
                    <span style="color: #8B949E;">Remaining Budget:</span>
                    <span style="color: {'#00E676' if remaining >= 0 else '#FF5252'}; font-weight: 700;">{_format_inr(remaining)}</span>
                </div>
                <div style="margin-bottom: 4px;">
                    <div style="display: flex; justify-content: space-between; color: #C9D1D9; font-size: 0.8rem;">
                        <span>Budget Utilization</span>
                        <span>{util:.1f}%</span>
                    </div>
                    <div style="background: rgba(255,255,255,0.1); border-radius: 999px; height: 8px; overflow: hidden; margin-top: 4px;">
                        <div style="background: {'#00E676' if util <= 90 else '#FFAB00' if util <= 100 else '#FF5252'}; width: {min(100.0, max(0.0, util))}%; height: 100%;"></div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # ---------------- ⚙️ PROJECT PROGRESS & BUDGET UPDATE EXPANDER ----------------
    with st.expander("✏️ Update Project Information & Progress"):
        with st.form("update_project_details_form"):
            up_c1, up_c2, up_c3 = st.columns(3)
            with up_c1:
                new_progress = st.number_input("Progress (%)", min_value=0.0, max_value=100.0, value=float(active_project.get("progress") or 0.0), step=1.0)
                p_status_options = ["Planning", "In Progress", "On Hold", "Completed", "Cancelled"]
                raw_p_status = active_project.get("status", "In Progress")
                if raw_p_status == "Active":
                    raw_p_status = "In Progress"
                p_status_idx = p_status_options.index(raw_p_status) if raw_p_status in p_status_options else 1
                new_status = st.selectbox("Status", p_status_options, index=p_status_idx)
            with up_c2:
                new_budget = st.number_input("Estimated Budget (INR ₹)", min_value=0.0, value=float(active_project.get("budget") or 0.0), step=100000.0)
                new_spending = st.number_input("Actual Spending (INR ₹)", min_value=0.0, value=float(active_project.get("actual_spending") or 0.0), step=100000.0)
            with up_c3:
                new_pm = st.text_input("Project Manager", value=active_project.get("project_manager") or "")
                new_loc = st.text_input("Location", value=active_project.get("location") or "")

            save_up = st.form_submit_button("💾 Save Project Updates", type="primary", use_container_width=True)
            if save_up:
                # Automatically mark Completed if progress reaches 100%
                if new_progress >= 100.0 and new_status != "Cancelled":
                    new_status = "Completed"

                with get_db() as conn:
                    models.update_project(
                        conn,
                        selected_project_id,
                        progress=new_progress,
                        status=new_status,
                        budget=new_budget,
                        actual_spending=new_spending,
                        project_manager=new_pm.strip(),
                        location=new_loc.strip(),
                    )
                st.success("✅ Project metrics updated successfully!")
                st.rerun()

    # ---------------- 🔍 TASK FILTERS & WORK SCHEDULE ----------------
    st.markdown("""
        <div class="hub-card" style="padding: 16px 20px; margin-bottom: 16px; margin-top: 10px;">
            <h4>🔍 Filters</h4>
            <span class="hub-card-tag">Narrow down active construction tasks for this project</span>
        </div>
    """, unsafe_allow_html=True)

    f_col1, f_col2 = st.columns([1, 1])
    with f_col1:
        status_filter = st.multiselect(
            "Filter by Status",
            options=["Completed", "In Progress", "Pending", "Not Started", "Delayed"],
            default=["Completed", "In Progress", "Pending", "Not Started", "Delayed"]
        )
    with f_col2:
        priority_filter = st.multiselect(
            "🚨 Filter by Priority",
            options=["Critical", "High", "Medium", "Low"],
            default=["Critical", "High", "Medium", "Low"]
        )

    task_records = [
        {
            "ID": t["id"],
            "Task": t["task_name"],
            "Status": t["status"],
            "Assignee": t["assignee"] or "",
            "Priority": t["priority"],
            "Progress (%)": t.get("progress", 0.0),
            "Start Date": t.get("start_date") or "",
            "Due Date": t.get("due_date") or "",
        }
        for t in tasks
    ]
    if not task_records:
        df = pd.DataFrame(columns=["ID", "Task", "Status", "Assignee", "Priority", "Progress (%)", "Start Date", "Due Date"])
    else:
        df = pd.DataFrame(task_records)

    if df.empty:
        filtered_df = df
    else:
        filtered_df = df[
            (df["Status"].isin(status_filter)) &
            (df["Priority"].isin(priority_filter))
        ]

    st.markdown("<h4 style='color: #00E5FF; margin: 20px 0 10px 0;'>📌 Active Work Schedule</h4>", unsafe_allow_html=True)

    st.dataframe(
        filtered_df,
        column_config={
            "ID": st.column_config.NumberColumn("Task ID", width="small"),
            "Task": st.column_config.TextColumn("Task Description", width="large"),
            "Status": st.column_config.SelectboxColumn(
                "Current Status", options=["Completed", "In Progress", "Pending", "Not Started", "Delayed"], width="medium", required=True
            ),
            "Assignee": st.column_config.TextColumn("Assigned Engineer", width="medium"),
            "Priority": st.column_config.SelectboxColumn(
                "Priority Level", options=["Critical", "High", "Medium", "Low"], width="medium", required=True
            ),
            "Progress (%)": st.column_config.ProgressColumn("Progress", min_value=0, max_value=100, format="%.0f%%"),
            "Start Date": st.column_config.TextColumn("Start Date", width="small"),
            "Due Date": st.column_config.TextColumn("Due Date", width="small"),
        },
        use_container_width=True,
        hide_index=True
    )

    # ---------------- 📌 TASK MANAGEMENT FORMS (ADD / EDIT / DELETE) ----------------
    t_tab1, t_tab2, t_tab3 = st.tabs(["➕ Add New Task", "✏️ Update Task", "🗑️ Delete Task"])

    with t_tab1:
        with st.form("add_task_form"):
            t_name = st.selectbox(
                "Construction Task Name *",
                [
                    "Site Preparation & Clearing",
                    "Excavation & Earthwork",
                    "Foundation Concrete Pouring",
                    "Footing & Substructure",
                    "Column Construction",
                    "Beam & Slab Formwork",
                    "RCC Reinforcement Steel Work",
                    "Masonry & Brickwork",
                    "Plumbing & Sanitation Setup",
                    "Electrical Wiring Phase 1",
                    "HVAC Ductwork Installation",
                    "Plastering & Interior Finishing",
                    "Site Safety Inspection Audit",
                    "Custom Construction Task",
                ]
            )
            custom_t_name = st.text_input("If Custom, enter Task Name", placeholder="Specify custom construction task...")
            t_name_final = custom_t_name.strip() if t_name == "Custom Construction Task" and custom_t_name.strip() else t_name

            tc1, tc2, tc3 = st.columns(3)
            with tc1:
                t_assignee = st.text_input("Assigned Engineer/Contractor", placeholder="e.g. John Doe")
                t_priority = st.selectbox("Priority", ["Critical", "High", "Medium", "Low"], index=2)
            with tc2:
                t_status = st.selectbox("Status", ["Not Started", "In Progress", "Completed", "Delayed"], index=1)
                t_prog = st.number_input("Task Progress (%)", min_value=0.0, max_value=100.0, value=0.0, step=5.0)
            with tc3:
                t_sdate = st.date_input("Start Date", value=datetime.date.today(), key="add_task_sdate")
                t_ddate = st.date_input("Due Date", value=datetime.date.today() + datetime.timedelta(days=30), key="add_task_ddate")

            submit_t = st.form_submit_button("📌 Add Construction Task", type="primary", use_container_width=True)

            if submit_t:
                if not t_name_final:
                    st.error("Please specify a valid task name.")
                elif t_ddate < t_sdate:
                    st.error("Due Date cannot be earlier than Start Date.")
                else:
                    if t_prog >= 100.0:
                        t_status = "Completed"
                    with get_db() as conn:
                        models.create_task(
                            conn,
                            task_name=t_name_final,
                            status=t_status,
                            assignee=t_assignee.strip(),
                            priority=t_priority,
                            project_id=selected_project_id,
                            start_date=t_sdate.isoformat(),
                            due_date=t_ddate.isoformat(),
                            progress=t_prog,
                        )
                    st.success(f"✅ Task '{t_name_final}' added to project!")
                    st.rerun()

    with t_tab2:
        if tasks:
            task_dict = {f"#{t['id']}: {t['task_name']} ({t['status']})": t for t in tasks}
            sel_t_label = st.selectbox("Select Task to Edit", list(task_dict.keys()), key="sel_task_to_edit")
            target_t = task_dict[sel_t_label]

            with st.form("edit_task_form"):
                et_c1, et_c2, et_c3 = st.columns(3)
                with et_c1:
                    et_status = st.selectbox(
                        "Status", ["Not Started", "In Progress", "Completed", "Delayed"],
                        index=["Not Started", "In Progress", "Completed", "Delayed"].index(target_t["status"]) if target_t["status"] in ["Not Started", "In Progress", "Completed", "Delayed"] else 1
                    )
                    et_priority = st.selectbox(
                        "Priority", ["Critical", "High", "Medium", "Low"],
                        index=["Critical", "High", "Medium", "Low"].index(target_t["priority"]) if target_t["priority"] in ["Critical", "High", "Medium", "Low"] else 2
                    )
                with et_c2:
                    et_assignee = st.text_input("Assigned Engineer", value=target_t.get("assignee") or "")
                    et_prog = st.number_input("Task Progress (%)", min_value=0.0, max_value=100.0, value=float(target_t.get("progress") or 0.0), step=5.0)
                with et_c3:
                    et_sdate = st.text_input("Start Date (YYYY-MM-DD)", value=target_t.get("start_date") or "")
                    et_ddate = st.text_input("Due Date (YYYY-MM-DD)", value=target_t.get("due_date") or "")

                save_t = st.form_submit_button("💾 Update Task", type="primary", use_container_width=True)
                if save_t:
                    if et_prog >= 100.0:
                        et_status = "Completed"
                    with get_db() as conn:
                        models.update_task(
                            conn,
                            target_t["id"],
                            status=et_status,
                            priority=et_priority,
                            assignee=et_assignee.strip(),
                            progress=et_prog,
                            start_date=et_sdate.strip(),
                            due_date=et_ddate.strip(),
                        )
                    st.success(f"✅ Task #{target_t['id']} updated successfully!")
                    st.rerun()
        else:
            st.info("No tasks available to edit.")

    with t_tab3:
        if tasks:
            task_del_dict = {f"#{t['id']}: {t['task_name']}": t["id"] for t in tasks}
            del_t_label = st.selectbox("Select Task to Delete", list(task_del_dict.keys()), key="sel_task_to_del")
            if st.button("🗑️ Confirm Delete Task", type="primary", use_container_width=True):
                with get_db() as conn:
                    models.delete_task(conn, task_del_dict[del_t_label])
                st.success("✅ Task deleted.")
                st.rerun()
        else:
            st.info("No tasks available to delete.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------- 🏁 PROJECT MILESTONES & RISKS ----------------
    m_col, r_col = st.columns([1, 1])

    with m_col:
        st.markdown("<h4 style='color: #00E5FF;'>🚩 Project Milestones</h4>", unsafe_allow_html=True)
        if milestones:
            m_df = pd.DataFrame(milestones)[["milestone_name", "target_date", "actual_date", "status"]]
            st.dataframe(
                m_df,
                column_config={
                    "milestone_name": st.column_config.TextColumn("Milestone"),
                    "target_date": st.column_config.TextColumn("Target Date"),
                    "actual_date": st.column_config.TextColumn("Actual Date"),
                    "status": st.column_config.SelectboxColumn("Status", options=["Upcoming", "In Progress", "Completed", "Delayed"]),
                },
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No milestones defined for this project.")

        with st.expander("➕ Add Milestone"):
            with st.form("add_milestone_form"):
                m_name = st.text_input("Milestone Name", placeholder="e.g. Structural Slab Pouring")
                m_tdate = st.date_input("Target Date", value=datetime.date.today() + datetime.timedelta(days=45))
                m_st = st.selectbox("Milestone Status", ["Upcoming", "In Progress", "Completed", "Delayed"])
                sub_m = st.form_submit_button("🚩 Add Milestone", type="primary", use_container_width=True)
                if sub_m and m_name.strip():
                    with get_db() as conn:
                        models.create_milestone(conn, selected_project_id, m_name.strip(), m_tdate.isoformat(), None, m_st)
                    st.success("✅ Milestone added!")
                    st.rerun()

    with r_col:
        st.markdown("<h4 style='color: #00E5FF;'>🛡️ Risks & Critical Issues</h4>", unsafe_allow_html=True)
        if issues:
            i_df = pd.DataFrame(issues)[["title", "severity", "responsible_person", "status"]]
            st.dataframe(
                i_df,
                column_config={
                    "title": st.column_config.TextColumn("Risk / Issue"),
                    "severity": st.column_config.SelectboxColumn("Severity", options=["Low", "Medium", "High", "Critical"]),
                    "responsible_person": st.column_config.TextColumn("Owner"),
                    "status": st.column_config.SelectboxColumn("Status", options=["Open", "In Progress", "Resolved"]),
                },
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No open risks or issues logged for this project.")

        with st.expander("➕ Report Risk / Issue"):
            with st.form("add_issue_form"):
                i_title = st.text_input("Issue Title", placeholder="e.g. Concrete Mixer Breakdown")
                i_desc = st.text_area("Issue Description", placeholder="Details about delay or impact...")
                ic1, ic2 = st.columns(2)
                with ic1:
                    i_sev = st.selectbox("Severity", ["Critical", "High", "Medium", "Low"], index=2)
                with ic2:
                    i_owner = st.text_input("Responsible Engineer", placeholder="e.g. Sarah Smith")
                sub_i = st.form_submit_button("🛡️ Log Risk/Issue", type="primary", use_container_width=True)
                if sub_i and i_title.strip():
                    with get_db() as conn:
                        models.create_project_issue(conn, selected_project_id, i_title.strip(), i_desc.strip(), i_sev, i_owner.strip(), "Open")
                    st.success("✅ Risk/Issue logged!")
                    st.rerun()

    # ---------------- 📄 PROJECT REPORT EXPORT ----------------
    st.markdown("<br><hr style='border:0; height:1px; background:rgba(255,255,255,0.1); margin: 20px 0;'>", unsafe_allow_html=True)
    rep_col1, rep_col2 = st.columns([3, 1])
    with rep_col1:
        st.markdown(f"<p style='color:#8B949E; font-size:0.9rem;'>Export complete executive report for <b>{active_project['name']}</b>.</p>", unsafe_allow_html=True)
    with rep_col2:
        report_text = f"""====================================================
CONSTRUCTION INTELLIGENCE HUB — PROJECT EXECUTIVE REPORT
====================================================
Project Name:       {active_project['name']}
Project ID:         #{active_project['id']}
Client Name:        {active_project.get('client_name') or 'N/A'}
Location:           {active_project.get('location') or 'N/A'}
Project Manager:    {active_project.get('project_manager') or 'N/A'}
Status:             {active_project.get('status')}
Project Health:     {health_title} ({health_desc})
Overall Progress:   {active_project.get('progress', 0.0):.1f}%
Estimated Budget:   {_format_inr(active_project.get('budget'))}
Actual Spending:    {_format_inr(active_project.get('actual_spending'))}
Remaining Budget:   {_format_inr(float(active_project.get('budget') or 0) - float(active_project.get('actual_spending') or 0))}
Total Tasks:        {tot_tasks} (Completed: {completed_cnt}, In Progress: {in_prog_cnt}, Pending: {pending_cnt})
Total Milestones:   {len(milestones)}
Open Risks/Issues:  {sum(1 for i in issues if i.get('status') != 'Resolved')}
Generated On:       {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
====================================================
"""
        st.download_button(
            label="📄 Export Project Report",
            data=report_text,
            file_name=f"project_{active_project['id']}_report.txt",
            mime="text/plain",
            use_container_width=True,
        )
