<div align="center">

# HRPulse

**Next-Generation AI-Powered Human Resources Platform**

*Where Human Resources Meets Artificial Intelligence*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

</div>

## Overview

HRPulse is a highly scalable, AI-driven Human Resources platform specifically engineered to bridge the gap between complex HR operations and non-technical end-users. It consolidates core HR responsibilities into a single pane of glass: Applicant Tracking (ATS), Employee Database Management, Actionable Analytics, and intuitive AI-assisted workflows via our omni-present assistant, **Aria**. 

## Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                     React + TypeScript + Vite               │
│               TailwindCSS • Recharts • Zustand              │
├─────────────────────────────────────────────────────────────┤
│                       FastAPI (Python 3.11)                 │
│              JWT Auth • Pydantic v2 • SQLAlchemy 2.0        │
├──────────────────────────────┬──────────────────────────────┤
│       AI Logic (Aria)        │            Data            │
│  LLM Contextual Processing   │        PostgreSQL 15       │
│  Prompt Engineering          │           Redis 7          │
└──────────────────────────────┴──────────────────────────────┘
```

## Features

| Feature | Description |
|---|---|
| **Command Dashboard** | Instant bird's-eye view of organizational health, KPIs, and recent activity. |
| **Employee Compendium** | A modernized, fuzzy-searchable directory with responsive employee profile cards. |
| **Actionable Analytics** | Dynamic SVG charting for retention curves, time-to-hire pipelines, and department distributions. |
| **Applicant Tracking System** | Kanban-style drag-and-drop board for seamless recruitment tracking. |
| **Floating Aria Agent** | Context-aware, jargon-free AI assistant accessible persistently to help users with HR queries. |
| **Platform Settings** | Enterprise-grade administration for theme preferences and user-level permissions. |

## Tech Stack

### Frontend
- React 18 + TypeScript & Vite
- TailwindCSS (Premium glassmorphism, light theme)
- Recharts (Data visualizations)
- Zustand (Client state) & context APIs
- React Router v6

### Backend
- Python 3.11 + FastAPI
- Pydantic v2 & SQLAlchemy 2.0
- Docker + PostgreSQL 15 & Redis 7
- PyTest for robust backend validation

### GenAI (Aria)
- Custom LLM endpoint integration with dynamic prompt engineering
- Context-aware querying based on the active UI view
- Strict "HR-only" boundary security to prevent hallucinations

### Infrastructure
- Docker & Docker Compose
- Microsoft Azure App Services & Azure Container Registry
- Automated CI/CD Pipelines

## Quick Start

### 1. Clone and configure

```bash
git clone <repository-url>
cd CapStone
cp .env.example .env
```

### 2. Start all services

Ensure Docker Desktop is running, then deploy the full stack:

```bash
docker-compose up --build
```

This command will:
- Spin up PostgreSQL and Redis.
- Apply database migrations automatically.
- Initialize the FastAPI backend (Port 8000).
- Launch the React frontend (Port 3000).

### 3. Open the application

| Service | URL |
|---|---|
| **Frontend** | [http://localhost:3000](http://localhost:3000) |
| **Backend API** | [http://localhost:8000](http://localhost:8000) |
| **API Docs (Swagger)** | [http://localhost:8000/docs](http://localhost:8000/docs) |

### 4. Default Credentials
- **Email:** `admin@hrpulse.com`
- **Password:** `admin123`

## Design System

HRPulse follows a luxury, minimalist "light theme" design language:
- **Background:** Crisp pure whites (`#FFFFFF`) to soft grays (`#F5F5F5`).
- **Typography:** Modern, highly legible numerical fonts paired with sans-serif elements.
- **Accents:** Subtle glassmorphism overlays with smooth 200ms transitions.
- **Accessibility:** Deep contrasts and full keyboard navigability built-in.

## Roadmap & Future Scope

While the MVP is complete and deployed, future developments include:
1. **Automated Payroll Integration:** Linking out to platforms like Stripe.
2. **Predictive Attrition AI:** Expanding analytics to analyze deeper sentiment patterns for attrition risk.
3. **Document Parsing:** Automatically extracting scoreable metadata from candidate CVs and pushing to the ATS.

## Deployment

The application is containerized and currently configured for deployment on **Microsoft Azure**, using Azure App Services, Azure Database for PostgreSQL, and Key Vault integration for managing environment connections securely.

## License

This project is a capstone submission. All rights reserved.

---

<div align="center">
  <sub>Built with precision by the HRPulse Development Team</sub>
</div>
