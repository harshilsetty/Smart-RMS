# Contributing to Smart RMS

Thank you for your interest in contributing to Smart RMS! This document outlines the process for contributing to this academic prototype.

## Local Setup

### 1. Environment
Copy the example environment file:
```bash
cp .env.example .env
```
Ensure that `INTEGRATION_MODE=mock` and `AI_PROVIDER=mock` for safe local testing.

### 2. Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 3. Frontend
```bash
cd frontend
npm install
npm run dev
```

## Branch Strategy
- `main` represents the production-ready prototype.
- Create feature branches named `feature/<feature-name>` or `fix/<bug-name>`.
- All merges to `main` require a Pull Request.

## Coding Expectations
- Maintain the **AI Assists, Humans Decide** principle. Do not implement autonomous AI decision making for high-impact actions.
- Ensure all new features are backed by synthetic test cases.
- PII must always be redacted before passing text to ML/LLM boundaries.

## Tests
All contributions must pass the existing backend and frontend test suites.
- Run backend tests: `pytest` from the `/backend` directory.
- Run frontend build: `npm run build` from the `/frontend` directory.

## Pull Request Expectations
Please use the PR template provided in `.github/PULL_REQUEST_TEMPLATE.md`.
All PRs should document the scope of changes, security/privacy considerations, and include UI screenshots if applicable.
