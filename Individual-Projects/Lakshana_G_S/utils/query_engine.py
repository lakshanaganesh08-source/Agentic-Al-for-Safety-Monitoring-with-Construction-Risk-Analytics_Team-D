import pandas as pd


# ==========================================================
# Helper
# ==========================================================

def contains(question, keywords):
    question = question.lower()
    return any(keyword in question for keyword in keywords)


# ==========================================================
# Query Engine
# ==========================================================

def answer_query(question, data):

    q = question.lower().strip()

    # =====================================================
    # Greetings
    # =====================================================

    greetings = [
        "hi",
        "hello",
        "hey",
        "good morning",
        "good afternoon",
        "good evening"
    ]

    if q in greetings:
        return (
            "Hello! 👋 Welcome to ConstructIQ AI.\n\n"
            "I can help you with:\n"
            "• Project Portfolio\n"
            "• Budget Analysis\n"
            "• Cost Estimation\n"
            "• Material Estimation\n"
            "• Delay Analysis\n"
            "• Rework Intelligence\n"
            "• Safety Analytics\n"
            "• Risk Intelligence\n"
            "• Construction Documents\n"
            "• Daily Reports\n\n"
            "How can I help you with your construction project today?"
        )

    if "thank" in q:
        return "You're welcome! Let me know if you need any project-related assistance."

    if q in ["bye", "exit", "goodbye"]:
        return "Thank you for using ConstructIQ AI. Have a productive day!"

    # =====================================================
    # Portfolio Summary
    # =====================================================

    if contains(q, [
        "summary",
        "portfolio",
        "overview",
        "dashboard"
    ]):

        projects = data["projects"]

        return f"""
Portfolio Summary

• Total Projects : {len(projects)}

• Total Budget : ₹ {projects['Budget_INR'].sum():,.0f}

• Actual Cost : ₹ {projects['Actual_Cost_INR'].sum():,.0f}

• Average Completion :
{projects['Completion_Percentage'].mean():.1f}%

• Budget Utilization :
{(projects['Actual_Cost_INR'].sum()/projects['Budget_INR'].sum())*100:.1f}%
"""

    # =====================================================
    # Highest Budget
    # =====================================================

    if contains(q, [
        "highest budget",
        "largest budget",
        "maximum budget",
        "costliest project"
    ]):

        p = data["projects"].loc[
            data["projects"]["Budget_INR"].idxmax()
        ]

        return f"""
Highest Budget Project

Project Name : {p['Project_Name']}
Project ID : {p['Project_ID']}
Client : {p['Client_Name']}
Budget : ₹ {p['Budget_INR']:,.0f}
Completion : {p['Completion_Percentage']}%
Priority : {p['Priority']}
"""

    # =====================================================
    # Number of Projects
    # =====================================================

    if contains(q, [
        "how many projects",
        "number of projects",
        "total projects"
    ]):

        return f"Total Projects : {len(data['projects'])}"

    # =====================================================
    # Budget Utilization
    # =====================================================

    if contains(q, [
        "budget utilization",
        "budget used",
        "utilization"
    ]):

        projects = data["projects"]

        util = (
            projects["Actual_Cost_INR"].sum()
            / projects["Budget_INR"].sum()
        ) * 100

        return f"Overall Budget Utilization : {util:.1f}%"

    # =====================================================
    # Delay
    # =====================================================

    if contains(q, [
        "delay",
        "delayed",
        "schedule"
    ]):

        delay = (
            data["delays"]
            .groupby("Project_ID")["Delay_Days"]
            .sum()
        )

        return f"""
Delay Analysis

Project with Maximum Delay :
{delay.idxmax()}

Delay :
{delay.max()} Days

Average Delay :
{data['delays']['Delay_Days'].mean():.1f} Days
"""

    # =====================================================
    # Rework
    # =====================================================

    if contains(q, [
        "rework",
        "quality",
        "defect"
    ]):

        df = data["rework"]

        return f"""
Construction Rework

Total Cases : {len(df)}

Resolved :
{len(df[df['Resolved']=='Yes'])}

Pending :
{len(df[df['Resolved']=='No'])}

Total Rework Cost :
₹ {df['Rework_Cost'].sum():,.0f}

Top Root Cause :
{df['Root_Cause'].mode()[0]}
"""

    # =====================================================
    # Safety
    # =====================================================

    if contains(q, [
        "safety",
        "helmet",
        "ppe"
    ]):

        score = data["safety"]["Overall_Safety_Score"].mean()

        return f"""
Safety Summary

Average Safety Score :
{score:.1f}

Overall site safety compliance is satisfactory.
"""

    # =====================================================
    # Risks
    # =====================================================

    if contains(q, [
        "risk",
        "hazard",
        "threat"
    ]):

        df = data["risks"]

        return df.head(10).to_string(index=False)

    # =====================================================
    # Documents
    # =====================================================

    if contains(q, [
        "document",
        "drawing",
        "certificate",
        "pending"
    ]):

        pending = data["documents"]

        pending = pending[
            pending["Status"] == "Pending Review"
        ]

        if pending.empty:
            return "There are no pending documents."

        return pending.to_string(index=False)

    # =====================================================
    # Materials
    # =====================================================

    if contains(q, [
        "material",
        "cement",
        "steel",
        "brick",
        "sand"
    ]):

        return data["estimation_materials"].to_string(index=False)

    # =====================================================
    # Daily Reports
    # =====================================================

    if contains(q, [
        "daily",
        "report",
        "progress",
        "workers",
        "weather"
    ]):

        return data["daily_reports"].head(10).to_string(index=False)

    # =====================================================
    # Unknown Question
    # =====================================================

    return None