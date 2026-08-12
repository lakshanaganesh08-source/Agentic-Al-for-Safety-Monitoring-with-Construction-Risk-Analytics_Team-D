# ==========================================================
# Context Engine
# ==========================================================

def get_context(question, data):

    q = question.lower()

    # =====================================================
    # PROJECTS
    # =====================================================

    if any(word in q for word in [

        "project",
        "portfolio",
        "client",
        "manager",
        "priority",
        "completion",
        "status",
        "budget"

    ]):

        return (
            "PROJECT DATA\n\n"
            + data["projects"].to_string(index=False)
        )

    # =====================================================
    # COST ESTIMATION
    # =====================================================

    elif any(word in q for word in [

        "cost",
        "estimate",
        "estimation",
        "expense",
        "budget utilization"

    ]):

        return (
            "COST ESTIMATION DATA\n\n"
            + data["cost_estimation"].to_string(index=False)
        )

    # =====================================================
    # MATERIAL ESTIMATION
    # =====================================================

    elif any(word in q for word in [

        "material",
        "cement",
        "steel",
        "brick",
        "sand",
        "paint",
        "aggregate"

    ]):

        return (
            "MATERIAL ESTIMATION DATA\n\n"
            + data["estimation_materials"].to_string(index=False)
        )

    # =====================================================
    # DELAYS
    # =====================================================

    elif any(word in q for word in [

        "delay",
        "late",
        "schedule",
        "timeline"

    ]):

        return (
            "DELAY DATA\n\n"
            + data["delays"].to_string(index=False)
        )

    # =====================================================
    # REWORK
    # =====================================================

    elif any(word in q for word in [

        "rework",
        "quality",
        "defect",
        "root cause"

    ]):

        return (
            "REWORK DATA\n\n"
            + data["rework"].to_string(index=False)
        )

    # =====================================================
    # SAFETY
    # =====================================================

    elif any(word in q for word in [

        "safety",
        "helmet",
        "ppe",
        "inspection"

    ]):

        return (
            "SAFETY DATA\n\n"
            + data["safety"].to_string(index=False)
        )

    # =====================================================
    # RISKS
    # =====================================================

    elif any(word in q for word in [

        "risk",
        "hazard",
        "threat",
        "mitigation"

    ]):

        return (
            "RISK DATA\n\n"
            + data["risks"].to_string(index=False)
        )

    # =====================================================
    # DOCUMENTS
    # =====================================================

    elif any(word in q for word in [

        "document",
        "drawing",
        "certificate",
        "approval",
        "report"

    ]):

        return (
            "DOCUMENT DATA\n\n"
            + data["documents"].to_string(index=False)
        )

    # =====================================================
    # DAILY REPORTS
    # =====================================================

    elif any(word in q for word in [

        "daily",
        "worker",
        "weather",
        "progress",
        "attendance"

    ]):

        return (
            "DAILY REPORT DATA\n\n"
            + data["daily_reports"].to_string(index=False)
        )

    # =====================================================
    # DEFAULT
    # =====================================================

    return (
        "PROJECT PORTFOLIO SUMMARY\n\n"

        f"Total Projects : {len(data['projects'])}\n"

        f"Total Budget : ₹ {data['projects']['Budget_INR'].sum():,.0f}\n"

        f"Actual Cost : ₹ {data['projects']['Actual_Cost_INR'].sum():,.0f}\n"

        f"Average Completion : "
        f"{data['projects']['Completion_Percentage'].mean():.1f}%\n\n"

        "PROJECT DATA\n\n"

        + data["projects"].head(10).to_string(index=False)
    )