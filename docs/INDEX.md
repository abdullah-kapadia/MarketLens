# MarketLens — Documentation Index

**All documentation for the MarketLens project, organized by scope.**

---

## Project-Level Documents

| # | Document | Path | Description |
|---|----------|------|-------------|
| 0 | **Root README** | [`README.md`](../README.md) | Project overview, architecture, quick start for both sub-projects |
| 1 | **PRD** | [`docs/PRD.md`](PRD.md) | Product Requirements Document — problem, vision, personas, features, success metrics |
| 2 | **Hackathon Plan** | [`docs/HACKATHON_PLAN.md`](HACKATHON_PLAN.md) | 4-day sprint plan with hour-by-hour breakdown, risk register, minimum viable demo |
| 3 | **Demo Script** | [`docs/DEMO_SCRIPT.md`](DEMO_SCRIPT.md) | 4-minute demo script, elevator pitch, Q&A answers, backup plans, slide deck outline |
| 4 | **API Contract** | [`docs/API_CONTRACT.md`](API_CONTRACT.md) | Definitive API specification — endpoints, SSE events, data models (Python + TypeScript), error codes |
| — | **This Index** | [`docs/INDEX.md`](INDEX.md) | You are here |

---

## Backend Documents

Located in `docs/backend-docs/` — specific to the `marketlens-backend` Python/FastAPI sub-project.

| # | Document | Path | Description |
|---|----------|------|-------------|
| 5 | **Backend README** | [`docs/backend-docs/README.md`](backend-docs/README.md) | Architecture, toolkit overview, quick start, project structure, API summary |
| 6 | **Implementation Plan** | [`docs/backend-docs/IMPLEMENTATION_PLAN.md`](backend-docs/IMPLEMENTATION_PLAN.md) | Module specifications, function signatures, output examples, config files, implementation order |
| 7 | **Tech Spec** | [`docs/backend-docs/TECH_SPEC.md`](backend-docs/TECH_SPEC.md) | Agent system prompt, 8 tool schemas (Anthropic format), ReAct loop details, chart spec, PDF template spec, LLM fallback |
| 8 | **Environment Setup** | [`docs/backend-docs/ENV_SETUP.md`](backend-docs/ENV_SETUP.md) | Prerequisites, installation, requirements.txt, .env variables, data setup, Docker, testing, troubleshooting |

---

## Frontend Documents

Located in `docs/frontend-docs/` — specific to the `marketlens-frontend` Next.js/TypeScript sub-project.

| # | Document | Path | Description |
|---|----------|------|-------------|
| 9 | **Frontend README** | [`docs/frontend-docs/README.md`](frontend-docs/README.md) | Reasoning panel feature, component guide, styling, SSE integration overview |
| 10 | **Implementation Plan** | [`docs/frontend-docs/IMPLEMENTATION_PLAN.md`](frontend-docs/IMPLEMENTATION_PLAN.md) | Component hierarchy, state management, SSE hook spec, API client, styling specs, implementation order |
| 11 | **Tech Spec** | [`docs/frontend-docs/TECH_SPEC.md`](frontend-docs/TECH_SPEC.md) | Component interfaces, SSE parsing, TypeScript types, performance considerations, responsive design |
| 12 | **Environment Setup** | [`docs/frontend-docs/ENV_SETUP.md`](frontend-docs/ENV_SETUP.md) | Prerequisites, dependencies, .env variables, Tailwind config, Docker, mock data mode, troubleshooting |

---

## Reading Order

### For a New Team Member

1. **[PRD.md](PRD.md)** — Understand what we're building and why
2. **[HACKATHON_PLAN.md](HACKATHON_PLAN.md)** — Understand the timeline and priorities
3. **[API_CONTRACT.md](API_CONTRACT.md)** — Understand the interface between frontend and backend
4. Then dive into your track (backend or frontend docs)

### For a Backend Developer

1. [PRD.md](PRD.md) → [API_CONTRACT.md](API_CONTRACT.md)
2. [Backend README](backend-docs/README.md) → [Implementation Plan](backend-docs/IMPLEMENTATION_PLAN.md)
3. [Tech Spec](backend-docs/TECH_SPEC.md) → [Env Setup](backend-docs/ENV_SETUP.md)

### For a Frontend Developer

1. [PRD.md](PRD.md) → [API_CONTRACT.md](API_CONTRACT.md)
2. [Frontend README](frontend-docs/README.md) → [Implementation Plan](frontend-docs/IMPLEMENTATION_PLAN.md)
3. [Tech Spec](frontend-docs/TECH_SPEC.md) → [Env Setup](frontend-docs/ENV_SETUP.md)

### For a Demo/Pitch

1. [PRD.md](PRD.md) (Sections 1–2 only) → [DEMO_SCRIPT.md](DEMO_SCRIPT.md)

---

## Cross-References

| Topic | Primary Document | Also Referenced In |
|-------|-----------------|-------------------|
| Feature requirements | [PRD.md](PRD.md) §4 | [HACKATHON_PLAN.md](HACKATHON_PLAN.md) |
| API endpoints | [API_CONTRACT.md](API_CONTRACT.md) §2 | [Backend README](backend-docs/README.md), [Frontend API client](frontend-docs/IMPLEMENTATION_PLAN.md) §5 |
| SSE event types | [API_CONTRACT.md](API_CONTRACT.md) §2.1 | [Frontend TECH_SPEC](frontend-docs/TECH_SPEC.md) §2 |
| Data models (Python) | [API_CONTRACT.md](API_CONTRACT.md) §3.1 | [Backend IMPLEMENTATION_PLAN](backend-docs/IMPLEMENTATION_PLAN.md) §2.12 |
| Data models (TypeScript) | [API_CONTRACT.md](API_CONTRACT.md) §3.1 | [Frontend TECH_SPEC](frontend-docs/TECH_SPEC.md) §3 |
| Agent tools (8 tools) | [Backend TECH_SPEC](backend-docs/TECH_SPEC.md) §1 | [Backend IMPLEMENTATION_PLAN](backend-docs/IMPLEMENTATION_PLAN.md) §2 |
| Agent system prompt | [Backend TECH_SPEC](backend-docs/TECH_SPEC.md) §1.1 | [PRD.md](PRD.md) §2.1 |
| Chart specification | [Backend TECH_SPEC](backend-docs/TECH_SPEC.md) §3 | [Backend IMPLEMENTATION_PLAN](backend-docs/IMPLEMENTATION_PLAN.md) §2.9 |
| PDF template | [Backend TECH_SPEC](backend-docs/TECH_SPEC.md) §4 | [Backend IMPLEMENTATION_PLAN](backend-docs/IMPLEMENTATION_PLAN.md) §2.10 |
| UI components | [Frontend TECH_SPEC](frontend-docs/TECH_SPEC.md) §1 | [Frontend IMPLEMENTATION_PLAN](frontend-docs/IMPLEMENTATION_PLAN.md) §7 |
| Styling/theme | [Frontend IMPLEMENTATION_PLAN](frontend-docs/IMPLEMENTATION_PLAN.md) §6 | [Frontend ENV_SETUP](frontend-docs/ENV_SETUP.md) §5.1 |
| Docker setup | Backend: [ENV_SETUP](backend-docs/ENV_SETUP.md) §8 | Frontend: [ENV_SETUP](frontend-docs/ENV_SETUP.md) §9 |
| Demo rehearsal | [DEMO_SCRIPT.md](DEMO_SCRIPT.md) | [HACKATHON_PLAN.md](HACKATHON_PLAN.md) Day 4 |

---

*Total: 12 documents + this index + root README = 14 files*
