<div align="center">

# 🧾 Zero-Touch GST ITC Recovery

**Automated GST Input Tax Credit reconciliation, optimization, and filing — powered by AI agents.**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org)
[![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white)](https://mongodb.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

---

*End-to-end ITC recovery pipeline — from ERP data ingestion to filing-ready GSTR-3B drafts — with zero manual intervention.*

</div>

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Repository Structure](#-repository-structure)
- [Getting Started](#-getting-started)
- [API Reference](#-api-reference)
- [Testing](#-testing)
- [Disclaimer](#%EF%B8%8F-disclaimer)
- [License](#-license)

---

## 🔍 Overview

Indian businesses lose billions annually due to **unclaimed or mismatched Input Tax Credit (ITC)** under the GST regime. Manual reconciliation between ERP purchase registers and GSTR-2B data is tedious, error-prone, and often results in missed credits.

**Zero-Touch GST ITC Recovery** solves this by orchestrating a multi-agent AI workflow that:

1. **Ingests** purchase data from ERP systems  
2. **Reconciles** it against GSTR-2B supplier filings  
3. **Identifies** eligible, blocked, and mismatched ITC  
4. **Optimizes** credit utilization strategy  
5. **Chases** vendors for missing invoices via email/WhatsApp  
6. **Drafts** filing-ready GSTR-3B returns  
7. **Exports** everything to a professional PDF report  

All of this happens through a single API call, with **real-time progress streaming** via Server-Sent Events (SSE).

---

## ✨ Key Features

| Feature | Description |
|---|---|
| **🤖 Agent-Based Workflow** | Five specialized agents (ERP, Reconciler, Optimizer, Vendor Chase, Filing) orchestrated via LangGraph |
| **📊 Smart Reconciliation** | Automatic matching of ERP purchase records against GSTR-2B with mismatch detection |
| **💡 ITC Optimization** | AI-driven recommendations for maximizing eligible credit and resolving blocked ITC |
| **📧 Vendor Communication** | Auto-generated chase emails and WhatsApp messages for non-compliant vendors |
| **📑 GSTR-3B Drafting** | Filing-ready return values computed from reconciled data |
| **📄 PDF Reports** | Professional, downloadable PDF reports via ReportLab |
| **⚡ Real-Time Streaming** | Live stage-by-stage progress updates via SSE |
| **📅 Dynamic Period Execution** | Run recovery for any `YYYY-MM` tax period |

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Next.js Frontend                         │
│              (React + TypeScript Dashboard)                     │
│         Recovery Dashboard  │  GSTR-3B Table View               │
└──────────────────────┬──────────────────────────────────────────┘
                       │  SSE / REST
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                             │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                  LangGraph Orchestrator                   │  │
│  │                                                           │  │
│  │   ┌──────────┐   ┌────────────┐   ┌───────────────┐       │  │
│  │   │ ERP Agent│──>│ Reconciler │──>│   Optimizer   │       │  │
│  │   └──────────┘   └────────────┘   └───────┬───────┘       │  │
│  │                                           │               │  │
│  │                           ┌───────────────▼────────────┐  │  │
│  │                           │      Vendor Chase Agent    │  │  │
│  │                           └───────────────┬────────────┘  │  │
│  │                                           │               │  │
│  │                           ┌───────────────▼────────────┐  │  │
│  │                           │      Filing Agent          │  │  │
│  │                           └────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │  GST Engine  │  │ PDF Service  │  │  Mock GSTN Service   │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
              ┌────────────────┐
              │    MongoDB     │
              │  (Persistence  │
              │ & Checkpoints) │
              └────────────────┘
```

### Agent Pipeline

| Stage | Agent | Responsibility |
|:---:|---|---|
| 1 | **ERP Agent** | Fetches and normalizes purchase register data from ERP/MongoDB |
| 2 | **Reconciler** | Matches ERP records against GSTR-2B; flags mismatches and missing invoices |
| 3 | **Optimizer** | Analyzes ITC eligibility, computes blocked credits, and generates optimization recommendations |
| 4 | **Vendor Chase** | Drafts follow-up communications (email/WhatsApp) for non-filing or mismatched vendors |
| 5 | **Filing Agent** | Computes GSTR-3B draft values and assembles the final filing-ready output |

---

## 🛠 Tech Stack

### Backend
- **[FastAPI](https://fastapi.tiangolo.com/)** — High-performance async API framework
- **[LangGraph](https://langchain-ai.github.io/langgraph/)** — Stateful multi-agent orchestration
- **[MongoDB](https://www.mongodb.com/)** — Document store for ERP data, states, and checkpoints
- **[ReportLab](https://www.reportlab.com/)** — PDF generation for filing reports
- **[Google Gemini](https://ai.google.dev/)** — LLM-powered agent reasoning *(optional)*
- **[Twilio](https://www.twilio.com/)** — WhatsApp message delivery *(optional)*

### Frontend
- **[Next.js](https://nextjs.org/)** + **React** + **TypeScript** — Modern SSR dashboard
- **Real-time SSE** — Live streaming of agent pipeline progress

---

## 📁 Repository Structure

```
zero-touch-gst-itc-recovery/
│
├── backend/
│   ├── agents/
│   │   ├── erp_agent.py          # ERP data ingestion agent
│   │   ├── reconciler.py         # GSTR-2B reconciliation agent
│   │   ├── optimizer_agent.py    # ITC optimization agent
│   │   ├── vendor_chase.py       # Vendor follow-up agent
│   │   └── filling_agent.py      # GSTR-3B filing agent
│   ├── mock_gstn/                # Simulated GSTN API for development
│   ├── main.py                   # FastAPI application entry point
│   ├── graph.py                  # LangGraph workflow definition
│   ├── state.py                  # Shared agent state schema
│   ├── db_schema.py              # MongoDB document models
│   ├── gst_engine.py             # Core GST computation engine
│   ├── pdf_service.py            # PDF report generator
│   └── seed_db.py                # Database seeding utility
│
├── frontend/
│   ├── app/                      # Next.js app router pages
│   ├── components/
│   │   ├── RecoveryDashboard.tsx  # Main recovery workflow UI
│   │   └── GSTR3BTable.tsx       # GSTR-3B table visualization
│   └── types/                    # TypeScript type definitions
│
├── tests/                        # Comprehensive test suite
│   ├── test_api.py               # API endpoint tests
│   ├── test_gst_engine.py        # GST engine unit tests
│   ├── test_reconciler.py        # Reconciliation logic tests
│   ├── test_erp_agent.py         # ERP agent tests
│   ├── test_filing_agent.py      # Filing agent tests
│   ├── test_pdf_service.py       # PDF generation tests
│   ├── test_models.py            # Data model tests
│   ├── test_edge_cases.py        # Edge case coverage
│   └── test_mock_gstn.py         # Mock GSTN API tests
│
├── LICENSE                       # MIT License
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.10+ |
| Node.js | 18+ |
| MongoDB | Running instance (local or Atlas) |

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/zero-touch-gst-itc-recovery.git
cd zero-touch-gst-itc-recovery
```

### 2. Configure Environment Variables

Create a `backend/.env` file:

```env
# Required
MONGODB_URI=mongodb://localhost:27017

# Optional — LLM-powered agents
GEMINI_API_KEY=your_gemini_api_key

# Optional — Vendor chase via WhatsApp
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
MY_WHATSAPP_NUMBER=whatsapp:+91XXXXXXXXXX

# Optional — Vendor chase via Email
SENDER_EMAIL=your_email@gmail.com
SENDER_APP_PASSWORD=your_app_password
```

### 3. Setup Backend

```bash
python -m venv .venv

# Windows
.\.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate

pip install --upgrade pip
pip install fastapi uvicorn pymongo python-dotenv pydantic \
  langgraph langgraph-checkpoint-mongodb langchain-google-genai \
  twilio reportlab pytest
```

### 4. Seed Sample Data

```bash
cd backend
python seed_db.py
cd ..
```

### 5. Setup Frontend

```bash
cd frontend
npm install
cd ..
```

### 6. Launch

Start both services in separate terminals:

```bash
# Terminal 1 — Backend
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

```bash
# Terminal 2 — Frontend
cd frontend
npm run dev
```

| Service | URL |
|---|---|
| Backend API | [`http://localhost:8000`](http://localhost:8000) |
| Frontend Dashboard | [`http://localhost:3000`](http://localhost:3000) |

---

## 📡 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `GET` | `/run-recovery-stream?period=YYYY-MM&days_to_cutoff=N` | Stream recovery pipeline execution via SSE |
| `POST` | `/run-recovery` | Run full recovery pipeline (non-streaming) |
| `POST` | `/generate-pdf` | Generate and download a filing-ready PDF report |
| `GET` | `/status/{thread_id}` | Fetch the status of a previous run |
| `GET` | `/mock-gstn/gstr2b/{period}` | Retrieve mock GSTR-2B data for development |

> 💡 **Tip:** Visit [`http://localhost:8000/docs`](http://localhost:8000/docs) for the interactive Swagger UI.

---

## 🧪 Testing

The project includes a comprehensive test suite covering agents, engine logic, API endpoints, models, and edge cases.

```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run a specific test file
python -m pytest tests/test_reconciler.py
```

---

## ⚠️ Disclaimer

> [!CAUTION]
> This is a **prototype** and is **not** a production-ready filing engine. All statutory outputs must be validated with a qualified tax professional before filing. Security hardening, input validation, and deployment controls must be implemented before any production use.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ for simplifying GST compliance in India**

</div>
