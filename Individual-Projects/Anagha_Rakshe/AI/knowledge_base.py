PROJECT_KNOWLEDGE = """
==========================================================
CONSTRUCTION INTELLIGENCE HUB
==========================================================

Construction Intelligence Hub is an AI-powered construction management platform
developed as part of Infosys Springboard Internship 7.0.

The purpose of the system is to assist construction managers,
site engineers and project teams in making faster and better
decisions using Artificial Intelligence.

==========================================================
PROJECT OBJECTIVES
==========================================================

The objectives are:

• Improve construction project management

• Reduce manual effort

• Automate report generation

• Analyze construction documents

• Detect project risks

• Improve construction site safety

• Estimate construction materials

• Provide an AI assistant for construction professionals

==========================================================
TECHNOLOGY STACK
==========================================================

Frontend

• Streamlit

Backend

• Python

Artificial Intelligence

• Ollama
• Llama 3.2

Libraries

• Plotly
• Pandas
• PyPDF

Styling

• HTML
• CSS

==========================================================
SYSTEM ARCHITECTURE
==========================================================

User

↓

Streamlit User Interface

↓

Python Backend

↓

Prompt Engineering

↓

Ollama

↓

Llama 3.2

↓

AI Response

==========================================================
PROJECT MODULES
==========================================================

1. Dashboard

Purpose:

Provides an overview of all construction activities.

Features:

• Project KPIs

• Charts

• Progress Monitoring

• AI Features

• Reports

----------------------------------------------------------

2. Projects Module

Purpose:

Manage construction projects.

Features:

• Project information

• Budget

• Timeline

• Status

• Progress

----------------------------------------------------------

3. Workers Module

Purpose:

Manage workforce information.

Features:

• Worker details

• Attendance

• Allocation

• Site assignment

----------------------------------------------------------

4. Construction Documentation Analysis

Purpose:

Analyze uploaded PDF construction documents.

Capabilities:

• Read PDFs

• Summarize documents

• Extract important information

• Explain technical documents

----------------------------------------------------------

5. Project Question Answering

Purpose:

Answer questions from uploaded project documents.

Workflow

Upload PDF

↓

Read PDF

↓

Extract text

↓

Ask Question

↓

AI Response

----------------------------------------------------------

6. Risk Detection

Purpose

Analyze construction risks.

Risk Types

• Budget Risk

• Material Risk

• Weather Risk

• Labour Risk

• Schedule Risk

Outputs

• Risk Level

• Recommendations

• Mitigation Strategies

----------------------------------------------------------

7. Site Safety

Purpose

Improve construction safety.

Provides

• Hazard Identification

• Safety Score

• PPE Recommendations

• Corrective Actions

• Emergency Preparedness

----------------------------------------------------------

8. Material Estimation

Purpose

Estimate required construction materials.

Materials

• Cement

• Sand

• Aggregate

• Steel

• Bricks

• Concrete

Outputs

• Estimated Quantity

• Assumptions

• Optimization Suggestions

----------------------------------------------------------

9. Daily Report Generator

Purpose

Automatically generate professional construction reports.

Contents

• Work Completed

• Workers

• Equipment

• Weather

• Delays

• Next Day Plan

----------------------------------------------------------

10. AI Construction Assistant

Purpose

Answer construction-related questions.

Capabilities

• Explain project modules

• Explain technologies

• Explain construction concepts

• Explain AI features

• Explain project workflow

==========================================================
WORKFLOW
==========================================================

User selects an AI module.

↓

User enters project information or uploads a PDF.

↓

Streamlit collects the input.

↓

Python processes the request.

↓

Prompt is generated.

↓

Ollama sends the prompt to Llama 3.2.

↓

Llama generates a response.

↓

The response is displayed to the user.

==========================================================
FEATURES
==========================================================

Construction Documentation Analysis

Project Question Answering

Daily Report Generator

Risk Detection

Site Safety

Material Estimation

AI Construction Assistant

Interactive Dashboard

==========================================================
ADVANTAGES
==========================================================

• Saves Time

• Reduces Manual Work

• Faster Decision Making

• Improved Safety

• Better Risk Analysis

• AI Powered Insights

==========================================================
LIMITATIONS
==========================================================

Current Version

• Local AI using Ollama

• Text-based Safety Analysis

• No Computer Vision

• Demo Dataset

==========================================================
FUTURE SCOPE
==========================================================

Computer Vision

YOLO PPE Detection

BIM Integration

IoT Sensors

Cloud Deployment

Predictive Analytics

Voice Assistant

Mobile Application

==========================================================
ABOUT STREAMLIT
==========================================================

Streamlit is an open-source Python framework used to build interactive
web applications quickly without requiring frontend development.

==========================================================
ABOUT OLLAMA
==========================================================

Ollama is a local AI model runtime that allows Large Language Models
such as Llama 3.2 to run on a local machine without internet access.

==========================================================
ABOUT LLAMA 3.2
==========================================================

Llama 3.2 is a Large Language Model developed by Meta.

In this project it is used for:

Document Analysis

Risk Detection

Material Estimation

Daily Report Generation

Construction Chatbot

Project Question Answering

==========================================================
IMPORTANT RULE
==========================================================

This assistant ONLY answers questions related to:

Construction

Construction Management

Construction Intelligence Hub

Civil Engineering Basics

Project Modules

Construction Technologies

Artificial Intelligence used in this project

Construction Safety

Material Estimation

Risk Detection

Construction Documents

If asked anything unrelated,
politely refuse.
"""

KNOWLEDGE_BASE = {
    "dashboard": """
Dashboard Module

Displays:
- KPIs
- Progress
- Charts
- AI Insights
- Reports
""",

    "risk": """
Risk Detection Module

Purpose:
Analyze construction risks.

Risk Types:
- Budget Risk
- Schedule Risk
- Weather Risk
- Material Risk
- Labour Risk

Outputs:
- Risk Level
- Mitigation Strategy
- Recommendations
""",

    "safety": """
Site Safety Module

Features:
- Hazard Detection
- PPE Recommendations
- Safety Score
- Corrective Actions
- Emergency Preparedness
""",

    "materials": """
Material Estimation Module

Estimates:
- Cement
- Steel
- Sand
- Aggregate
- Bricks
- Concrete

Provides optimization suggestions and assumptions.
""",

    "documents": """
Document Analysis Module

Supports:
- PDF Upload
- Text Extraction
- Summarization
- Key Information Extraction
""",

    "reports": """
Daily Report Module

Generates:

- Work Completed
- Workers
- Equipment
- Weather
- Delays
- Next Day Plan
""",

    "workers": """
Workers Module

Maintains:

- Worker Information
- Attendance
- Allocation
- Site Assignment
""",

    "project": """
Construction Intelligence Hub

Built using:

- Python
- Streamlit
- Ollama
- Llama 3.2
- Plotly
- Pandas
- PyPDF

Purpose:

AI-powered construction management platform.
"""
}