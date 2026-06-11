# Clausely — Legal Compilation Engine for India

### Google for Startups AI Agents Challenge 2026

**Track:** Build Net-New Agent  
**Prize Pool:** $90,000  

---

## The Problem

Indian courts reject **8–15% of legal filings** for preventable formatting errors.  
**1.7 million advocates. 200+ million documents per year. Zero AI tools designed for Indian courts.**

A cheque dishonour notice with 2.8cm margins instead of 3.0cm gets returned at the registry counter. An affidavit without a verification clause is rejected on the spot. Every rejection costs an advocate time, money, and reputation.

## What Clausely Does

Clausely is a **legal compilation engine** — it **compiles** legal intent into deterministic, registry-accepted court documents. Unlike generic AI tools that generate text, Clausely generates **validated legal artifacts**.

Think of it as a **compiler for law**: natural language goes in, court-ready documents come out.

```
Legal Intent → [Clausely ADK Pipeline] → Court-Ready Document
                    ├── Drafter Agent (Gemini 1.5 Flash)
                    ├── Acceptor Agent (Registry Simulation)
                    ├── Strategist (7-Agent Adversarial Swarm)
                    └── Case Base (Firestore Memory Bank)
```

## Google ADK Architecture

Clausely uses **4 ADK agents** coordinated by a `SequentialAgent` orchestrator:

```
clausely_orchestrator (SequentialAgent)
├── case_base_agent      → ADK Memory Bank + Firestore
├── drafter_agent        → Gemini 1.5 Flash + SFE tools
├── acceptor_agent       → Registry simulation + procedural linting
└── strategist_agent     → ParallelAgent (7-agent adversarial swarm)
    ├── petitioner_agent → Argues strongest case
    ├── opponent_agent   → Finds every weakness
    ├── reviewer_agent   → Checks legal accuracy
    ├── verifier_agent   → Verifies statute citations
    ├── objector_agent   → Procedural objections
    ├── presenter_agent  → Strategy synthesis
    └── judge_agent      → Scores probability of success
```

## ADK Features Used

| ADK Feature | How Clausely Uses It |
|---|---|
| `SequentialAgent` | Orchestrates intake → draft → validate → store pipeline |
| `ParallelAgent` | Runs 7 adversarial agents simultaneously in Strategist |
| `Agent` with `FunctionTool` | Drafter, Acceptor, Case Base agents with custom tools |
| `InMemorySessionService` | Session management for stateful agent conversations |
| `Runner` | Executes the multi-agent pipeline end-to-end |

## The Core Innovation — Symbolic Formatting Engine (SFE)

The SFE is **NOT an LLM**. It is a **deterministic rule engine** that enforces court formatting as immutable constraints.

```
LLM generates content → SFE enforces format → Registry accepts document
```

This is the architectural insight: **separate the probabilistic generation problem from the deterministic formatting problem**. Solve each with the right tool.

The SFE enforces:
- **Exact margins** (3.0cm left, 2.5cm right for Maharashtra District Courts)
- **Correct fonts** (Times New Roman, 14pt body)
- **Line spacing** (1.5× for District, 2.0× for High Court)
- **Mandatory sections** (cause title, verification, prayer, etc.)
- **Stamp paper values** (₹100 for MH-District, ₹10 for Delhi)
- **Section ordering** (court-mandated sequence)

## The Moat — Self-Evolving RL Pipeline

Every filing outcome feeds back into the system:

| Outcome | Reward Signal |
|---------|---------------|
| Registry accepted | **+3.0** |
| Document filed | +0.5 |
| Minor advocate edit | +0.5 |
| Major advocate edit | +0.2 |
| Registry rejected | **-3.0** |

These signals accumulate in Firestore and compound over time. The system gets more accurate with every Indian court filing. **The moat deepens with every user.**

## Business Case

| Metric | Value |
|--------|-------|
| **Market** | India, 1.7M advocates, ₹35,000 Crore legal services market |
| **Problem** | ₹0 spent on legal tech per document currently. All manual. |
| **Price** | ₹999/month (Advocate) · ₹4,999/month (Chambers) · $200/seat (Enterprise) |
| **CAC** | ₹2,000 via bar association partnerships |
| **LTV** | ₹36,000 (3-year) |
| **Founder** | Manas Khobrekar, Nagpur. Built for his mother — a practicing advocate. |

## Supported Jurisdictions

- 🏛️ Maharashtra District Court (`MH-DISTRICT`)
- 🏛️ Bombay High Court (`MH-HC`)
- 🏛️ Delhi District Court (`DL-DISTRICT`)
- 🏛️ Supreme Court of India (`IN-SC`)

## Tech Stack

- **Backend:** Python 3.11, FastAPI, Google ADK
- **AI:** Gemini 1.5 Flash (drafting & strategy analysis)
- **Frontend:** Streamlit (demo) 
- **Database:** Firestore (Case Base + Reward Signals)
- **Deployment:** Google Cloud Run
- **Export:** PDF (ReportLab) + DOCX (python-docx)

## How to Run

```bash
# Clone
git clone https://github.com/[username]/clausely-adk
cd clausely-adk

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Set credentials
cp .env.example .env
# Edit .env with your GOOGLE_API_KEY

# Run Streamlit demo
streamlit run app/streamlit_app.py

# Or run FastAPI backend
uvicorn app.main:app --reload --port 8080

# Run tests
pytest tests/ -v
```

## Deployment (Cloud Run)

```bash
# Build and deploy
gcloud builds submit --config cloudbuild.yaml

# Or manual Docker deploy
docker build -t clausely-adk .
docker run -p 8080:8080 clausely-adk
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/compile` | POST | Full ADK multi-agent compilation |
| `/api/v1/validate` | POST | Quick SFE-only validation |
| `/api/v1/export` | POST | PDF/DOCX export |
| `/api/v1/reward` | POST | Log RL reward signal |
| `/api/v1/stats` | GET | Aggregate reward statistics |
| `/api/v1/jurisdictions` | GET | List supported jurisdictions |
| `/health` | GET | Health check |

## Project Structure

```
clausely-adk/
├── agents/                 # ADK Agent definitions
│   ├── orchestrator.py     # Root SequentialAgent
│   ├── drafter.py          # Document generation agent
│   ├── acceptor.py         # Registry simulation agent
│   ├── strategist.py       # 7-agent adversarial swarm
│   └── case_base.py        # Firestore memory agent
├── tools/                  # Core tools & engines
│   ├── sfe.py              # Symbolic Formatting Engine (THE moat)
│   ├── legal_ast.py        # Legal Abstract Syntax Tree
│   ├── registry_rules.py   # Court filing rules database
│   ├── corpus_client.py    # IndianKanoon API wrapper
│   └── reward_signal.py    # RL reward signal logger
├── data/                   # Court rules & templates
│   ├── court_formats/      # JSON rules per jurisdiction
│   └── templates/          # Document templates
├── app/                    # Application interfaces
│   ├── main.py             # FastAPI backend
│   └── streamlit_app.py    # Streamlit demo frontend
├── tests/                  # Test suite
├── demo/                   # Demo materials
├── Dockerfile              # Cloud Run container
├── cloudbuild.yaml         # CI/CD config
└── requirements.txt        # Python dependencies
```

---

**Built with ❤️ in Nagpur, India.**  
*For every advocate who ever got a filing rejected for the wrong margin.*
