# Construction Intelligence Hub

An AI-powered web application for construction project monitoring, cost and delay
prediction, safety analytics, computer-vision site scanning, and AI-assisted reporting —
built with Python and Streamlit.

## Features

- **Dashboard** — portfolio-wide KPIs, budget vs. actual cost, status split, safety trend.
- **Cost Prediction** — Random Forest regression forecasting final project cost & overrun.
- **Delay Risk Prediction** — Random Forest classifier estimating schedule risk (Low/Medium/High).
- **Vision Scanner** — OpenCV-based PPE coverage and surface-crack indicator analysis on site photos.
- **AI Assistant** — TF-IDF + cosine-similarity chatbot answering questions from live project data.
- **About** — architecture and technology overview.

> Project Management, Safety Analytics, and AI Reports modules are part of the original
> design but not yet implemented in this build.

## Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Project Structure

```
construction_intelligence_hub/
├── app.py
├── requirements.txt
├── README.md
├── .streamlit/config.toml
├── utils/
│   ├── data_gen.py       # synthetic project dataset + FAQ data
│   ├── ml_models.py      # cost & delay Random Forest pipelines
│   └── styling.py        # shared CSS + hero/section/kpi components
└── modules/
    ├── dashboard.py
    ├── cost_prediction.py
    ├── delay_prediction.py
    ├── cv_module.py
    ├── chatbot.py
    └── about.py
```

## Disclaimer

All project, cost, and safety data is procedurally generated for demonstration purposes.
Predictions are illustrative outputs of models trained on synthetic data and should not be
used for real financial or safety decisions.
