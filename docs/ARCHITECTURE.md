# Architecture

# Architectural Style

The initial application uses a modular monolith.

The backend is a FastAPI application with explicit service boundaries.

The frontend is a React application communicating with the backend through HTTP APIs.

---

# High-Level Architecture

```text
┌─────────────────────────────────────────────┐
│               React Frontend                │
│                                             │
│ Resume │ Profile │ Jobs │ Analysis │ Editor │
└──────────────────────┬──────────────────────┘
                       │
                    HTTP/JSON
                       │
┌──────────────────────▼──────────────────────┐
│                FastAPI Backend              │
│                                             │
│  API Layer                                  │
│      │                                      │
│      ▼                                      │
│  Application / Domain Services              │
│      │                                      │
│      ├───────────────┬───────────────────┐  │
│      ▼               ▼                   ▼  │
│ Persistence      AI Services       Document │
│                                    Services │
│      │               │                      │
└──────┼───────────────┼──────────────────────┘
       │               │
       ▼               ├──────────────┐
 PostgreSQL            ▼              ▼
 + pgvector        LLM Provider   Embedding Model