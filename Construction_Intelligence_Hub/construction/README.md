# 🏗️ Construction Intelligence Hub

An AI-powered Streamlit dashboard for construction project management with 7 modules:

1. **Document Analyzer** – Upload PDFs/DOCX/TXT (contracts, BOQs, tenders) and get instant structured insights + AI summaries.
2. **Project Questionnaire** – Client intake form to capture project scope, budget, timeline.
3. **Risk Detection** – Flags budget, soil, timeline, and location-based risks.
4. **Site Safety** – Daily safety checklist + incident logging.
5. **Material Estimation (AI)** – Enter sq.ft → get cement, steel, sand, bricks, cost estimate instantly.
6. **Construction Chatbot** – Domain-locked chatbot ("BuildBot") connected to a local **Llama** model via **Ollama** — only answers construction questions.
7. **Daily Report Generator** – Generates a clean, client-ready daily progress report.

---

## 📁 Project Structure

```
construction_hub/
├── app.py                      # Main entry point (sidebar navigation)
├── requirements.txt
├── README.md
├── .streamlit/
│   └── config.toml             # Theme colors
├── assets/
│   └── style.css               # Custom CSS styling
├── modules/
│   ├── document_analyzer.py
│   ├── project_questionnaire.py
│   ├── risk_detection.py
│   ├── site_safety.py
│   ├── material_estimation.py
│   ├── chatbot.py
│   └── daily_report.py
└── utils/
    ├── llama_client.py          # Talks to local Llama (Ollama) + topic guardrails
    └── material_calculator.py   # Thumb-rule material/cost estimator
```

---

## ✅ Step-by-Step Setup

### Step 1 — Install Python dependencies
```bash
cd construction_hub
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2 — Install Ollama (to run Llama locally, for real AI answers)
This is what powers the Chatbot, Document Analyzer's AI summary, Material Estimation's AI explanation, and the Daily Report Generator.

1. Download & install Ollama: https://ollama.com/download
2. Pull a Llama model (choose based on your machine's RAM):
   ```bash
   ollama pull llama3        # ~8B model, needs ~8GB RAM
   # or a lighter model:
   ollama pull llama3.2:3b
   ```
3. Ollama runs a local server automatically at `http://localhost:11434`.
   You can verify it's running with:
   ```bash
   ollama list
   ```

> If you skip this step, the app still works — the Chatbot and AI features will
> show a friendly "Ollama not found" message and fall back to simple offline answers,
> and Material Estimation's core calculator (sq.ft → materials) works with **no AI server needed at all**.

### Step 3 — Run the app
```bash
streamlit run app.py
```
Open the URL shown in your terminal (usually `http://localhost:8501`).

---

## 🔒 How the Chatbot stays "construction only"

`utils/llama_client.py` enforces this in two layers:
1. **Keyword pre-filter** – obviously off-topic messages never reach the model.
2. **System prompt** – instructs Llama to decline any non-construction question,
   even if the keyword filter lets a borderline message through.

You can expand `CONSTRUCTION_KEYWORDS` in `utils/llama_client.py` to widen/narrow scope.

---

## 🎨 Customizing the look

- Colors/theme: edit `.streamlit/config.toml` and `assets/style.css`
  (`--brand-orange`, `--bg-deep`, etc. are CSS variables at the top of `style.css`).
- Sidebar modules: edit the `MODULES` dictionary in `app.py` — order, icons, and names all come from there.

---

## 🧱 About the Material Estimation logic

`utils/material_calculator.py` uses standard **thumb-rule coefficients** per sq.ft
(cement bags, steel kg, sand/aggregate cft, bricks, paint, tiles, labour man-days),
scaled by a quality tier (Economy / Standard / Premium) and number of floors.
These are quick early-stage estimates — always confirm the final BOQ with a
structural engineer / quantity surveyor before ordering materials.

---

## 🛠️ Troubleshooting

| Issue | Fix |
|---|---|
| `ModuleNotFoundError: pdfplumber` or `docx` | Run `pip install -r requirements.txt` again |
| Chatbot says "couldn't reach Llama server" | Run `ollama serve` and make sure a model is pulled (`ollama pull llama3`) |
| Streamlit page blank/white | Refresh, or restart with `streamlit run app.py` |
| Want a different model | Change the "Ollama model tag" field inside the Chatbot page (e.g. `llama3.1`, `llama3.2:3b`) |
