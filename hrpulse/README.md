<div align="center">

# HRPulse

**AI-Powered Autonomous HR Intelligence Platform**

*Where Human Resources Meets Artificial Intelligence*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

</div>

## Overview

HRPulse is a fullstack web platform that empowers HR managers with AI-driven insights. Upload employee data, get ML/DL predictions (attrition risk, sentiment analysis, skill gap detection, performance forecasting), interact with autonomous AI agents, and watch multi-agent workflows execute in real time — all through a luxury editorial-style dashboard.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     React + TypeScript + Vite                │
│                     TailwindCSS • Recharts • Zustand         │
├─────────────────────────────────────────────────────────────┤
│                        FastAPI (Python 3.11)                 │
│              JWT Auth • Pydantic v2 • SQLAlchemy 2.0         │
├──────────────┬──────────────┬────────────────────────────────┤
│   ML/DL      │   GenAI      │   Data                         │
│  XGBoost     │  LangChain   │  PostgreSQL 15                 │
│  DistilBERT  │  LangGraph   │  Redis 7                       │
│  PyTorch     │  LlamaIndex  │  FAISS                         │
│  scikit-learn│  Ollama      │  MLflow                        │
│  SHAP        │  (Llama 3.1) │                                │
└──────────────┴──────────────┴────────────────────────────────┘
```

## Features

| Feature | Description |
|---|---|
| **Attrition Prediction** | XGBoost classifier with SHAP explainability per employee |
| **Sentiment Analysis** | DistilBERT NLP on employee feedback surveys |
| **Skill Gap Detection** | TF-IDF + KMeans clustering against job descriptions |
| **Performance Forecast** | LSTM neural network predicting next-quarter KPIs |
| **Policy Q&A Agent** | RAG-powered chatbot over HR policy documents |
| **Retention Agent** | Autonomous workflow: risk analysis → email draft → manager alert |
| **Recruitment Agent** | Resume parsing → skill matching → interview scheduling |
| **Onboarding Agent** | Auto-generates 30/60/90 day plans for new hires |
| **Pipeline Orchestrator** | Full autonomous workflow chaining all agents via LangGraph |

## Tech Stack

### Frontend
- React 18 + TypeScript
- Vite (build tool)
- TailwindCSS (custom luxury design tokens)
- Recharts (monochrome data visualizations)
- TanStack React Query (server state)
- Zustand (client state)
- React Router v6 (routing)
- Axios (HTTP client)

### Backend
- Python 3.11
- FastAPI (async web framework)
- Pydantic v2 (validation)
- SQLAlchemy 2.0 (async ORM)
- Alembic (database migrations)
- Celery + Redis (async task queue)
- python-jose (JWT authentication)

### ML/DL
- XGBoost (attrition classification)
- HuggingFace Transformers — DistilBERT (sentiment)
- scikit-learn (TF-IDF, KMeans clustering)
- PyTorch (LSTM performance forecasting)
- SHAP (model explainability)
- MLflow (experiment tracking)

### GenAI & Agents
- LangChain (LLM framework)
- LangGraph (agent orchestration)
- LlamaIndex (document indexing)
- FAISS (local vector store)
- Ollama + Llama 3.1 8B (local LLM — free, no API key)

### Infrastructure
- Docker + Docker Compose
- PostgreSQL 15 (via Docker)
- Redis 7 (via Docker)
- MLflow (via Docker)

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (v20+)
- [Ollama](https://ollama.com/) (for local LLM — optional, app has mock fallback)
- Git

## Quick Start

### 1. Clone and configure

```bash
git clone <repository-url>
cd hrpulse
cp .env.example .env
```

### 2. (Optional) Install Ollama and pull the model

```bash
# Download and install Ollama from https://ollama.com/
ollama pull llama3.1:8b
```

> **Note:** If Ollama is not running, all agent features will use mock responses so the application still functions fully.

### 3. Start everything with one command

```bash
docker-compose up --build
```

This will:
- Start PostgreSQL and Redis
- Run database migrations via Alembic
- Seed 500 employees, feedback surveys, job descriptions, resumes, HR policies, and performance history
- Train and save all ML models
- Start the FastAPI backend on port 8000
- Start the React frontend on port 3000
- Start MLflow tracking UI on port 5001

### 4. Open the application

| Service | URL |
|---|---|
| **Frontend** | [http://localhost:3000](http://localhost:3000) |
| **Backend API** | [http://localhost:8000](http://localhost:8000) |
| **API Docs (Swagger)** | [http://localhost:8000/docs](http://localhost:8000/docs) |
| **MLflow UI** | [http://localhost:5001](http://localhost:5001) |

### 5. Login

Use the pre-seeded credentials:
- **Email:** `admin@hrpulse.com`
- **Password:** `admin123`

## Project Structure

```
hrpulse/
├── docker-compose.yml          # All services orchestration
├── .env.example                # Environment template
├── .env                        # Local environment (gitignored)
├── README.md
│
├── frontend/                   # React + TypeScript + Vite
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   ├── pages/              # Route-level page components
│   │   ├── store/              # Zustand state management
│   │   ├── hooks/              # Custom React hooks
│   │   ├── api/                # Axios API layer
│   │   ├── types/              # TypeScript interfaces
│   │   └── styles/             # Global CSS + Tailwind config
│   ├── index.html
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   └── Dockerfile
│
├── backend/                    # Python FastAPI
│   ├── app/
│   │   ├── main.py             # FastAPI entry point
│   │   ├── api/                # Route handlers
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   ├── services/           # Business logic layer
│   │   ├── ml/                 # ML model training & inference
│   │   ├── agents/             # LangGraph agent definitions
│   │   └── core/               # Config, database, security
│   ├── seed_data.py            # Mock data generation & seeding
│   ├── requirements.txt
│   ├── alembic.ini
│   └── Dockerfile
│
└── ml_models/                  # Saved trained models (.pkl, .pt)
```

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/login` | Login with email/password |
| POST | `/api/auth/refresh` | Refresh JWT token |

### Employees
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/employees` | List all employees (paginated, filterable) |
| GET | `/api/employees/{id}` | Get single employee details |
| GET | `/api/employees/{id}/predictions` | Get all predictions for an employee |

### Predictions
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/predictions/attrition` | Run attrition risk prediction |
| POST | `/api/predictions/sentiment` | Run sentiment analysis |
| POST | `/api/predictions/skillgap` | Run skill gap analysis |
| POST | `/api/predictions/performance` | Run performance forecast |
| GET | `/api/predictions/dashboard-summary` | Dashboard aggregated metrics |

### Uploads
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/upload/csv` | Upload employee CSV data |
| POST | `/api/upload/resume` | Upload candidate resume PDF |
| POST | `/api/upload/policy-doc` | Upload HR policy document |

### Agents
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/agents/policy-qa` | Ask HR policy questions (RAG) |
| POST | `/api/agents/retention` | Run retention workflow for employee |
| POST | `/api/agents/recruitment` | Score resume against job description |
| POST | `/api/agents/onboarding` | Generate onboarding plan |
| POST | `/api/agents/run-pipeline` | Run full autonomous pipeline |
| GET | `/api/agents/pipeline-status` | SSE stream of pipeline progress |

## Design System

HRPulse follows a luxury editorial design language inspired by Rolex × Zara × H&M × Louis Vuitton:

- **Background:** `#FFFFFF` (pure white)
- **Text:** `#0A0A0A` (near black)
- **Surface:** `#F5F5F5` (light gray)
- **Accent:** `#C9A96E` (warm gold — used sparingly)
- **Headings:** Playfair Display (serif)
- **Body:** Inter (sans-serif)
- **Borders:** 1px solid `#E8E8E8`
- **Border radius:** max 4px
- **Transitions:** 200ms ease (no bounce, no scale)
- **Charts:** Monochrome palette with single gold accent

## Development

### Running services individually

```bash
# Backend only
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend only
cd frontend
npm install
npm run dev

# Database only
docker-compose up postgres redis -d
```

### Running tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Deployment

This project is designed to deploy to **Azure Student Subscription (free tier)**. See the deployment guide in Step 11 for:
- Azure App Service (backend)
- Azure Static Web Apps (frontend)
- Azure Database for PostgreSQL (flexible server)
- Azure Cache for Redis
- Azure OpenAI (replaces local Ollama)
- Azure Blob Storage (file uploads)

## License

This project is a capstone submission. All rights reserved.

---

<div align="center">
  <sub>Built with precision by HRPulse Team</sub>
</div>
