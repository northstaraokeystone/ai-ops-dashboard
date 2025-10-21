# Fulcrum

<p align="center">The agent-literate command center that unifies triage, diagnosis, and one-click remediation with a built-in audit trail.</p>

<p align="center">
  <a href="https://github.com/YOUR_ORG/YOUR_REPO/actions/workflows/ci.yml">
    <img alt="Build Status" src="https://img.shields.io/github/actions/workflow/status/YOUR_ORG/YOUR_REPO/ci.yml?branch=main&style=for-the-badge&logo=github">
  </a>
  <a href="https://github.com/northstaraokeystone/ai-ops-dashboard">
    <img alt="License" src="https://img.shields.io/github/license/YOUR_ORG/YOUR_REPO?style=for-the-badge&logo=apache">
  </a>
  <a href="https://pypi.org/project/fulcrum/">
    <img alt="PyPI Version" src="https://img.shields.io/pypi/v/fulcrum?style=for-the-badge&logo=pypi">
  </a>
</p>

---

## The Problem

Fragmented incident response across many tools slows Mean Time to Recovery (MTTR) and leaves AI agent actions unaudited and hard to explain, blocking compliance and trust in autonomous systems. When an agent fails, teams are left scrambling between observability platforms, ticketing systems, and runbook automators, wasting critical time while risks compound.

## The Solution

Fulcrum provides a unified **"Trust Command Center"** that brings together incident triage, automated diagnosis, and one-click remediation in a single, agent-aware surface. Built as an open-source platform, it provides a verifiable, immutable ledger for every agentic action and a simple Python SDK to make your agents resilient and observable in minutes.

This reduces resolution time, enhances auditability, and builds deep, provable trust in your agentic workforce.

## Core Features

*   **Verifiable Ledger:** Log every agentic action to an immutable, time-series ledger, ready for audit and analysis.
*   **Interactive Triage:** A single command center to investigate, assign ownership, and manage the lifecycle of incidents.
*   **Automated Remediation:** Execute pre-defined, version-controlled playbooks with one click directly from the UI.
*   **Python SDK:** A simple, clean SDK to integrate Fulcrum's resilience and observability capabilities into any AI agent in under 5 minutes.

## Getting Started

To get the Fulcrum stack running locally for development:

**1. Clone the Repository:**

git clone https://github.com/northstaraokeystone/ai-ops-dashboard
cd YOUR_REPO

2. Launch Services with Docker:
This command starts the PostgreSQL database and all other required backend services.

docker-compose up -d

3. Set up and Run the Backend API:
This will install dependencies and start the FastAPI server on localhost:8000.



# Activate virtual environment
python -m venv .venv
source .venv/bin/activate  # or .\.venv\Scripts\activate on Windows

# Install dependencies
pip install -r api/requirements.txt

# Run database migrations
alembic upgrade head

# Start the server
uvicorn api.main:app --reload
4. Run the Frontend:
Open a new terminal to run the React development server on localhost:5173.

Bash

cd frontend
npm install
npm run dev
You can now access the Trust Command Center at http://localhost:5173.

Contributing
We welcome contributions! Please see our CONTRIBUTING.md file for details on how to get started, our code standards, and the PR process.
