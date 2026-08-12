import re

# ==========================================================
# Greetings
# ==========================================================

GREETINGS = {

    "hi",
    "hii",
    "hello",
    "hey",
    "good morning",
    "good afternoon",
    "good evening",
    "thanks",
    "thank you",
    "bye",
    "goodbye"

}

# ==========================================================
# Allowed Construction Topics
# ==========================================================

PROJECT_KEYWORDS = [

    # General
    "project",
    "construction",
    "site",
    "client",
    "contractor",
    "engineer",
    "manager",

    # Cost
    "budget",
    "cost",
    "estimate",
    "estimation",
    "expense",

    # Materials
    "material",
    "cement",
    "steel",
    "sand",
    "brick",
    "concrete",
    "aggregate",
    "paint",

    # Schedule
    "delay",
    "timeline",
    "schedule",
    "progress",
    "completion",

    # Rework
    "rework",
    "quality",
    "defect",

    # Safety
    "safety",
    "helmet",
    "ppe",
    "inspection",
    "accident",

    # Risk
    "risk",
    "hazard",
    "mitigation",

    # Documents
    "document",
    "drawing",
    "approval",
    "certificate",
    "report",

    # Daily Reports
    "daily",
    "worker",
    "weather",
    "attendance",

    # AI Modules
    "portfolio",
    "dashboard",
    "analytics",

    # Dataset fields
    "project id",
    "project name",
    "priority",
    "status",
    "budget utilization",
    "actual cost",
    "completion percentage"

]

# ==========================================================
# Greeting Detection
# ==========================================================

def is_greeting(message: str) -> bool:

    if not message:
        return False

    msg = message.strip().lower()

    return msg in GREETINGS


# ==========================================================
# Project Query Detection
# ==========================================================

def is_project_query(message: str) -> bool:

    if not message:
        return False

    msg = message.lower()

    msg = re.sub(r"[^a-z0-9 ]", " ", msg)

    for keyword in PROJECT_KEYWORDS:

        if keyword in msg:
            return True

    return False


# ==========================================================
# Guardrail
# ==========================================================

def validate_query(message: str):

    """
    Returns

    (True, "greeting")
    (True, "project")
    (False, rejection_message)
    """

    if is_greeting(message):

        return (
            True,
            "greeting"
        )

    if is_project_query(message):

        return (
            True,
            "project"
        )

    return (

        False,

        """
🚧 ConstructIQ AI Scope Boundary

I can assist only with construction project-related information.

I can help with:

* Project Portfolio
* Budget & Cost Analysis
* Material Estimation
* Delay Prediction
* Risk Intelligence
* Construction Documents
* Daily Reports

Please ask a construction project-related question.
"""
    )