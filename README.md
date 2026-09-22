# FutureSelf AI — Your Friendly 30-Year Life & Wealth Companion

> **Empowering young adults (ages 20–25) to visually plan, understand, and achieve financial freedom before age 50 or 55.**

---

## 🌟 Overview

**FutureSelf AI** is an intelligent, human-centric life planning application designed to answer the fundamental question:
*"What will it take financially for me to buy a home, get married, raise children, invest wisely, and retire comfortably in the next 25–30 years?"*

Designed specifically for users with zero financial background, FutureSelf AI replaces intimidating jargon (*CAGR, FIRE Corpus, Inflation Matrix*) with friendly everyday language (*Annual Wealth Growth Speed, Freedom Bank Target, Future Price Check*), interactive on-demand tooltips, visual milestone charts, and an encouraging AI Co-Pilot powered by Google Cloud's **Agent Development Kit (ADK)** and **Vertex AI Agent Platform**.

---

## 🚀 Live Application Endpoints

- **Public Web Application (Cloud Run)**: [https://futureself-web-253558192043.us-east1.run.app](https://futureself-web-253558192043.us-east1.run.app)
- **Vertex AI Agent Runtime ID**: `projects/253558192043/locations/us-east1/reasoningEngines/7575663702678962176`
- **Agent Card URL (A2A Protocol)**: `https://us-east1-aiplatform.googleapis.com/reasoningEngines/v1/projects/253558192043/locations/us-east1/reasoningEngines/7575663702678962176/api/a2a/app/.well-known/agent-card.json`
- **Public Assets Bucket**: `gs://futureself-assets-qwiklabs-gcp-01-bb263000f5c6`

---

## 🎯 5-Step Guided Life Roadmap Wizard

The application breaks down complex long-term planning into 5 engaging, bite-sized steps:

1. **Step 1: Life & Wealth Baseline**
   - User inputs current age (e.g., 23), target freedom age (e.g., 50), monthly earnings, and monthly savings.
2. **Step 2: Major Life Milestones**
   - Planned purchase age and budget for vehicles and a dream home or land property.
3. **Step 3: Family & Education Standards**
   - Marriage age, wedding budget, number of kids, and education tier (*Standard Local, Premier National, or Top Global University*).
4. **Step 4: Investment Growth Engines**
   - Allocation across Company Stocks (S&P 500 funds), Real Estate/Land, Gold & Safe Assets, and Digital Assets (Crypto).
5. **Step 5: 360° Life Roadmap & AI Co-Pilot**
   - Consolidates total accumulated wealth at retirement, calculates the **Freedom Bank Target**, projects monthly passive income payouts, displays a 30-year wealth chart, and launches the AI Co-Pilot.

---

## 💡 Key Design Innovations

### 1. On-Demand Interactive Education
- **`💡 Why does this matter?` Expandable Drawers**: Static placards are replaced by smooth collapsible drawers that stay hidden until clicked, keeping the interface clean and spacious.
- **`ℹ️` Hover Tooltips**: Hovering over any slider or chip reveals plain-English explanations without taking up screen real estate.

### 2. Plain Everyday Language
- `CAGR` → **Annual Wealth Growth Speed**
- `FIRE Corpus` → **Freedom Bank Target**
- `Inflation Matrix` → **Future Price Check**
- `S&P 500 Index` → **Company Stocks & Shared Funds**

---

## 🛠️ Enterprise Google Cloud Tech Stack

FutureSelf AI integrates a full suite of enterprise Google Cloud features:

| Feature | Service / Component | Purpose |
| :--- | :--- | :--- |
| **Agent Framework** | `google.adk` (Agent Development Kit) | Core agent structure, function tools, and callbacks |
| **Reasoning Engine** | **Vertex AI Agent Platform** | Managed serverless agent runtime (`us-east1`) |
| **Long-Term Memory** | **Vertex AI Memory Bank Service** | Remembers facts, goals, and user preferences across distinct sessions |
| **Dream Goal Visualizer**| **Generative AI (`gemini-3.1-flash-lite-image`)** | Generates visuals of dream goals (homes, vehicles) published to GCS |
| **Public Asset Bucket** | **Google Cloud Storage (GCS)** | Public bucket (`futureself-assets-...`) serving image assets |
| **Persistent Storage** | **Cloud Storage JSON Database** | Saves and reloads 30-year financial blueprints (`blueprints/{user_id}/`) |
| **Live Market API** | `https://api.frankfurter.dev` + CPI Data | Fetches live benchmark exchange rates, S&P 500 CAGR, and inflation data |
| **Grounded Guides** | **Vertex AI RAG Engine Architecture** | Document-grounded Q&A for Roth IRA vs 401(k), 20% down payments, and taxes |
| **Web Proxy & UI** | **FastAPI + Cloud Run** | Public HTTPS web interface communicating via A2A protocol |

---

## 📁 Repository Structure

```
FutureSelf/
├── app/
│   └── agent.py              # Root ADK agent, tools, Memory Bank callbacks, and prompt instructions
├── frontend/
│   ├── main.py               # FastAPI proxy (supports local ADK runner & Cloud Run A2A mode)
│   ├── Dockerfile            # Container definition for Cloud Run deployment
│   ├── requirements.txt      # Python dependencies for the proxy container
│   └── static/
│       └── index.html        # 5-Step interactive wizard, tooltips, chart canvas, and AI chat feed
├── pyproject.toml            # ADK project manifest and virtual environment config
├── agents-cli-manifest.yaml  # Deployment configuration for Agent Platform
└── README.md                 # Complete technical & functional documentation
```

---

## 🏃 Local Development & Testing

### 1. Run Local Web Proxy & Dev Environment
```bash
uv run python frontend/main.py
```
Open `http://localhost:8080` in your browser.

### 2. Deploy Agent to Vertex AI Agent Platform
```bash
agents-cli deploy --no-confirm-project
```

### 3. Deploy Web Frontend to Cloud Run
```bash
gcloud run deploy futureself-web \
  --source ./frontend \
  --region us-east1 \
  --quiet \
  --allow-unauthenticated \
  --set-env-vars="AGENT_ENGINE_RESOURCE_NAME=projects/253558192043/locations/us-east1/reasoningEngines/7575663702678962176,AGENT_DIRECTORY=app"
```

---

## 🏆 Project Achievements & Impact

- **Democratized Financial Literacy**: Translates wall-street math into simple visual steps for young adults starting their careers.
- **Full Cloud & AI Integration**: Combines LLM reasoning, long-term memory, generative media, live web APIs, and persistent storage into one cohesive application.
- **Enterprise-Ready Deployment**: Fully shipped on Google Cloud infrastructure (Vertex AI Agent Runtime + Cloud Run).
